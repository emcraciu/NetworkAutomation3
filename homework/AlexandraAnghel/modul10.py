import asyncio
import telnetlib3
import re
import time
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Pattern

HOST = "92.81.55.146"
PORT = 5051

USERNAME = None
PASSWORD = None
ENABLE_PASSWORD = None

PRUNE_EXTRAS = False
LOG_PATH = Path("/tmp/ios_telnet_transcript.log")

ANSI_RE: Pattern[str] = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")

def clean(s: str) -> str:
    s = ANSI_RE.sub("", s)
    return s.replace("\r", "")

def now() -> str:
    return time.strftime("%H:%M:%S")

class TelnetConnection:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.reader = None
        self.writer = None
        self.prompt_hash = "#"   # will be updated after detect
        self.prompt_more = "--More--"
        self.prompt_user = "Username:"
        self.prompt_pass = "Password:"
        self.prompt_enable = "Password:"
        self.last_buf = ""
        LOG_PATH.write_text("", encoding="utf-8")

    def log(self, msg: str) -> None:
        with LOG_PATH.open("a", encoding="utf-8") as f:
            f.write(f"[{now()}] {msg}\n")

    async def connect(self):
        self.reader, self.writer = await telnetlib3.open_connection(
            self.host, self.port, encoding="utf8", connect_minwait=0.05
        )
        self.log(f"CONNECTED to {self.host}:{self.port}")

    def write(self, data: str):
        self.log(f">>> {data}")
        self.writer.write(data + "\r\n")

    async def read_chunk(self, n: int = 8192, step_timeout: float = 0.8) -> str:
        try:
            out = await asyncio.wait_for(self.reader.read(n), timeout=step_timeout)
            out = clean(out or "")
            if out:
                self.last_buf += out
                self.log(f"<<< {out}")
            return out
        except asyncio.TimeoutError:
            return ""

    async def expect_regex(self, pattern: Pattern[str], timeout: float = 10.0) -> str:
        end = time.monotonic() + timeout
        buf = ""
        while time.monotonic() < end:
            chunk = await self.read_chunk()
            if chunk:
                buf += chunk
                if pattern.search(buf):
                    return buf
            else:
                await asyncio.sleep(0.05)
        raise TimeoutError(f"Timeout waiting for /{pattern.pattern}/\nLast buffer:\n{buf}")

    async def send_expect(self, cmd: Optional[str], pattern: Pattern[str], pause: float = 0.0, timeout: float = 10.0) -> str:
        if cmd is not None:
            self.write(cmd)
        if pause:
            await asyncio.sleep(pause)
        return await self.expect_regex(pattern, timeout=timeout)

PROMPT_RE = re.compile(r"([^\s#>]+)[#>]\s*$", re.M)
MORE_RE   = re.compile(r"--More--", re.M)

def desired_blocks() -> Dict[str, List[str]]:
    return {
        "ip domain-name lab.local": [],
        "username admin privilege 15 secret P@rolaFort@": [],
        "ip ssh version 2": [],
        "crypto key generate rsa modulus 2048": [],
        "interface Ethernet0/0": ["ip address 10.0.0.1 255.255.255.0", "no shutdown"],
        "interface Ethernet0/1": ["ip address 10.0.1.1 255.255.255.0", "no shutdown"],
        "line vty 0 4": ["transport input ssh", "login local"],
    }

async def detect_prompt(conn: TelnetConnection) -> str:
    for _ in range(3):
        conn.write("")  # wake
        buf = await conn.expect_regex(PROMPT_RE, timeout=6.0)
        m = list(PROMPT_RE.finditer(buf))
        if m:
            prompt = m[-1].group(0).strip()
            host = m[-1].group(1)
            conn.log(f"DETECTED PROMPT: {prompt} (host={host})")
            conn.prompt_hash = "#"
            return host
    raise RuntimeError("Could not detect device prompt. See transcript log.")

async def page_more(conn: TelnetConnection):
    # If --More-- appears, send space to continue
    if MORE_RE.search(conn.last_buf):
        conn.write(" ")
        await asyncio.sleep(0.1)

async def login_if_needed(conn: TelnetConnection):
    conn.write("")
    await asyncio.sleep(0.4)
    splash = await conn.read_chunk()
    if "Press RETURN" in splash:
        conn.write("")
        await asyncio.sleep(0.4)

    if "Username:" in conn.last_buf or "username:" in conn.last_buf:
        if not USERNAME or not PASSWORD:
            raise RuntimeError("Console asks for credentials. Set USERNAME/PASSWORD at the top.")
        conn.write(USERNAME)
        await conn.expect_regex(re.compile("Password:", re.M), timeout=6.0)
        conn.write(PASSWORD)
        await asyncio.sleep(0.5)

async def enter_enable(conn: TelnetConnection, hostname: str):
    tail = conn.last_buf.splitlines()[-1:] or [""]
    if tail[0].strip().endswith(">"):
        conn.write("enable")
        if ENABLE_PASSWORD or PASSWORD:
            await conn.expect_regex(re.compile("Password:", re.M), timeout=6.0)
            conn.write(ENABLE_PASSWORD or PASSWORD or "")
        await conn.expect_regex(re.compile(rf"{re.escape(hostname)}#", re.M), timeout=8.0)

async def get_running_config(conn: TelnetConnection, hostname: str) -> str:
    await conn.send_expect("terminal length 0", re.compile(rf"{re.escape(hostname)}#", re.M))
    conn.last_buf = ""  # reset for pagination checks
    await conn.send_expect("show running-config", re.compile(rf"{re.escape(hostname)}#", re.M), pause=0.3, timeout=20.0)
    # drain any extra chunks for big configs (and handle --More--)
    for _ in range(40):
        await page_more(conn)
        chunk = await conn.read_chunk(step_timeout=0.3)
        if not chunk:
            break
    text = conn.last_buf
    lines = [ln.rstrip() for ln in text.splitlines() if not ln.strip().startswith("show running-config")]
    return "\n".join(lines).strip()

def parse_blocks(text: str) -> Dict[str, List[str]]:
    blocks: Dict[str, List[str]] = {}
    header: Optional[str] = None
    for raw in text.splitlines():
        line = raw.rstrip()
        if not line:
            continue
        if not line[:1].isspace():
            header = line.strip()
            blocks[header] = []
        else:
            if header is not None:
                blocks[header].append(line.strip())
    return blocks

def diff_blocks(desired: Dict[str, List[str]], current: Dict[str, List[str]]) -> Tuple[List[Tuple[str, List[str]]], List[Tuple[str, List[str]]]]:
    to_add: List[Tuple[str, List[str]]] = []
    to_remove: List[Tuple[str, List[str]]] = []
    for h, want_children in desired.items():
        if h not in current:
            to_add.append((h, want_children.copy()))
        else:
            cur_children = current[h]
            missing = [c for c in want_children if c not in cur_children]
            if missing:
                to_add.append((h, missing))
    if PRUNE_EXTRAS:
        for h, cur_children in current.items():
            if h in desired:
                want_children = desired[h]
                extra = [c for c in cur_children if c not in want_children]
                if extra:
                    to_remove.append((h, extra))
    return to_add, to_remove

def build_cli_from_diff(hostname: str, to_add: List[Tuple[str, List[str]]], to_remove: List[Tuple[str, List[str]]]) -> List[str]:
    cmds: List[str] = ["conf t"]
    for h, children in to_add:
        if h.startswith(("hostname ",)):
            # change hostname first so prompts update
            cmds.insert(1, h)
            continue
        if h.startswith(("interface ", "line ", "router ", "ip dhcp pool ")):
            cmds.append(h)
            cmds.extend(children)
            cmds.append("exit")
        else:
            if children:
                cmds.append(h)
                cmds.extend(children)
                cmds.append("exit")
            else:
                cmds.append(h)
    if PRUNE_EXTRAS:
        for h, children in to_remove:
            if h.startswith(("interface ", "line ", "router ")):
                cmds.append(h)
                cmds.extend([f"no {c}" for c in children])
                cmds.append("exit")
            else:
                if children:
                    cmds.append(h)
                    cmds.extend([f"no {c}" for c in children])
                    cmds.append("exit")
    cmds.append("end")
    cmds.append("write memory")
    return cmds

async def apply_cli(conn: TelnetConnection, hostname: str, commands: List[str]):
    for c in commands:
        if c == "conf t":
            expect = re.compile(r"\(config\)#")
        elif c.startswith("hostname "):
            expect = re.compile(r"\(config\)#")
        elif c.startswith("interface "):
            expect = re.compile(r"\(config-if\)#")
        elif c.startswith("line "):
            expect = re.compile(r"\(config-line\)#")
        elif c.startswith(("router ", "ip dhcp pool ")):
            expect = re.compile(r"\(config")
        elif c in ("end", "write memory"):
            expect = re.compile(r"#")
        else:
            expect = re.compile(r"#")
        await conn.send_expect(c, expect, timeout=15.0)
        if c.startswith("hostname "):
            new_host = c.split(" ", 1)[1].strip()
            hostname = new_host  # for subsequent steps

async def main():
    conn = TelnetConnection(HOST, PORT)
    await conn.connect()
    await login_if_needed(conn)
    hostname = await detect_prompt(conn)
    await enter_enable(conn, hostname)
    # include hostname in desired, using whatever we detected
    desired = {"hostname " + hostname: []}
    desired.update(desired_blocks())
    running = await get_running_config(conn, hostname)
    current = parse_blocks(running)
    to_add, to_remove = diff_blocks(desired, current)
    if not to_add and (not PRUNE_EXTRAS or not to_remove):
        print("Device is already in desired state.")
        print(f"Transcript saved to: {LOG_PATH}")
        return
    cli = build_cli_from_diff(hostname, to_add, to_remove)
    print("\n=== CLI PLAN ===")
    for c in cli:
        print(c)
    await apply_cli(conn, hostname, cli)
    print("\nDevice synchronized to desired configuration.")
    print(f"Transcript saved to: {LOG_PATH}")

if __name__ == "__main__":
    asyncio.run(main())
