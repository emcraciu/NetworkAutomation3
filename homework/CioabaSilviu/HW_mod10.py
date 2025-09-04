import asyncio
from pathlib import Path
import telnetlib3

HOST = "92.81.55.146"
DEVICES = {
5186: r"C:\\Users\\silvi\\Desktop\\IOU.txt",
5114: r"C:\\Users\\silvi\\Desktop\\IOS.txt",
}

PROMPTS = ("#", ">", "(config)#", "(config-if)#")

def read_baseline(path: str) -> list[str]:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Nu găsesc baseline: {p}")
    lines = p.read_text(encoding="utf-8", errors="ignore").splitlines()
    return [ln.rstrip() for ln in lines if ln.strip() and not ln.strip().startswith("!")]

def split_blocks(lines: list[str]) -> dict[str, list[str]]:
    blocks, i, n = {}, 0, len(lines)
    while i < n:
        ln = lines[i]
        if ln and not ln.startswith(" "):
            head = ln
            i += 1
            subs = []
            while i < n and (lines[i].startswith(" ") or lines[i].startswith("\t")):
                subs.append(lines[i].lstrip())
                i += 1
            blocks[head] = subs
        else:
            i += 1
    return blocks

def build_delta(baseline_text: str, running_text: str) -> list[str]:
    bl_blocks = split_blocks([ln for ln in baseline_text.splitlines() if ln.strip()])
    rn_blocks = split_blocks([ln for ln in running_text.splitlines() if ln.strip()])

    cmds: list[str] = []

    for head, bl_subs in bl_blocks.items():
        rn_subs = rn_blocks.get(head)
        if rn_subs is None:
            cmds.append(head)
            cmds += [" " + s for s in bl_subs]
            continue
        add_subs = [s for s in bl_subs if s not in rn_subs]
        del_subs = [s for s in rn_subs if s not in bl_subs]
        if add_subs or del_subs:
            cmds.append(head)
            cmds += [" " + s for s in add_subs]
            cmds += [" no " + s for s in del_subs]

    for head in rn_blocks.keys() - bl_blocks.keys():
        cmds.append(head)
        if head.lower().startswith("interface "):
            cmds.append(" shutdown")
        else:
            cmds.append(" no " + head)

    return cmds


class Telnet:
    def __init__(self, host: str, port: int):
        self.host, self.port = host, port
        self.r = None
        self.w = None

    async def connect(self):
        self.r, self.w = await telnetlib3.open_connection(self.host, self.port)

    def send(self, line: str):
        if not line.endswith("\r\n"):
            line += "\r\n"
        self.w.write(line)

    async def drain(self):
        await self.w.drain()

    async def wait_prompt(self, timeout=12):
        buf, loop = "", asyncio.get_running_loop()
        end = loop.time() + timeout
        while True:
            if any(p in buf for p in PROMPTS):
                return buf
            if loop.time() > end:
                return buf
            chunk = await self.r.read(4096)
            if not chunk:
                await asyncio.sleep(0.05)
            else:
                buf += chunk

    async def wake(self):
        self.send("")
        await self.drain()
        await self.wait_prompt(2)

    async def show_run(self) -> str:
        self.send("terminal length 0")
        await self.drain()
        await self.wait_prompt(3)
        self.send("show running-config")
        await self.drain()
        return await self.wait_prompt(20)

    async def apply(self, cmds: list[str]):
        if not cmds:
            return
        self.send("configure terminal"); await self.drain(); await self.wait_prompt(5)
        for ln in cmds:
            self.send(ln if not ln.startswith(" ") else ln.lstrip())
            await self.drain()
            await self.wait_prompt(5)
        self.send("end")
        await self.drain()
        await self.wait_prompt(5)
        self.send("write memory")
        await self.drain()
        await self.wait_prompt(10)

    def close(self):
        try:
            if self.w:
                self.w.close()
        except Exception:
            pass


async def backup_running(port: int, out_file: str):
    t = Telnet(HOST, port)
    try:
        await t.connect()
        await t.wake()
        txt = await t.show_run()
        Path(out_file).parent.mkdir(parents=True, exist_ok=True)
        Path(out_file).write_text(txt, encoding="utf-8", errors="ignore")
        print(f"[{port}] backup -> {out_file}")
    finally:
        t.close()

async def reconcile(port: int, baseline_path: str):
    baseline_text = Path(baseline_path).read_text(encoding="utf-8", errors="ignore")
    t = Telnet(HOST, port)
    try:
        await t.connect(); await t.wake()
        running_text = await t.show_run()
        cmds = build_delta(baseline_text, running_text)
        if not cmds:
            print(f"[{port}] deja conform")
            return
        print(f"[{port}] aplic {len(cmds)} linii...")
        await t.apply(cmds)
        print(f"[{port}] OK")
    finally:
        t.close()


async def main():
    await asyncio.gather(*(backup_running(p, f"backups/{p}_running.txt") for p in DEVICES))
    await asyncio.gather(*(reconcile(p, DEVICES[p]) for p in DEVICES))
    await asyncio.gather(*(backup_running(p, f"post/{p}_running.txt") for p in DEVICES))

asyncio.run(main())



