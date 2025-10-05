import asyncio
import telnetlib3

HOST = "92.81.55.146"
PORTS = [5186, 5114]

PROMPTS = ("IOSV#", "IOU1#", "#", ">")

class TelnetConnection:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.reader = None
        self.writer = None

    async def connect(self, timeout=10):
        try:
            self.reader, self.writer = await asyncio.wait_for(
                telnetlib3.open_connection(self.host, self.port),
                timeout=timeout
            )
        except Exception as e:
            raise RuntimeError(f"connect failed on {self.port}: {e}")

    def write(self, data: str):
        if not data.endswith("\r\n"):
            data = data + "\r\n"
        self.writer.write(data)

    async def drain(self):
        await self.writer.drain()

    async def read_until_any(self, tokens, timeout=8):
        buf = ""
        end = asyncio.get_running_loop().time() + timeout
        while True:
            # dacă deja avem un token
            if any(t in buf for t in tokens):
                return buf
            # timeout?
            if asyncio.get_running_loop().time() > end:
                raise asyncio.TimeoutError("prompt wait timeout")
            chunk = await self.reader.read(1024)
            if not chunk:
                await asyncio.sleep(0.1)
            else:
                buf += chunk

    async def wake_prompt(self, attempts=3):
        last = ""
        for _ in range(attempts):
            self.write("")
            await self.drain()
            try:
                last = await self.read_until_any(PROMPTS, timeout=3)
                if any(p in last for p in PROMPTS):
                    return last
            except asyncio.TimeoutError:
                continue
        return last

    async def configure(self):
        try:
            banner = await self.wake_prompt()
            if not any(p in banner for p in PROMPTS):
                raise RuntimeError("no prompt detected")

            is_iosv = "IOSV#" in banner
            is_iou1 = "IOU1#" in banner

            self.write("terminal length 0"); await self.drain()
            await self.read_until_any(PROMPTS)

            self.write("configure terminal"); await self.drain()
            await self.read_until_any(("#", "(config)#"))

            if is_iosv:
                iface = "g0/0"
                ip = "192.168.200.2 255.255.255.0"
                host_prompt = ("IOSV(config-if)#",)
                end_prompt = ("IOSV#",)
            elif is_iou1:
                iface = "e0/0"
                ip = "192.168.200.3 255.255.255.0"
                host_prompt = ("IOU1(config-if)#",)
                end_prompt = ("IOU1#",)
            else:
                iface = "e0/0"
                ip = "192.168.200.2 255.255.255.0"
                host_prompt = ("(config-if)#", "#")
                end_prompt = ("#", ">")

            self.write(f"interface {iface}"); await self.drain()
            await self.read_until_any(host_prompt)

            self.write(f"ip address {ip}"); await self.drain()
            await self.read_until_any(host_prompt)

            self.write("no shutdown"); await self.drain()
            await self.read_until_any(host_prompt)

            self.write("exit"); await self.drain()
            await self.read_until_any(("(config)#", "#"))

            self.write("end"); await self.drain()
            await self.read_until_any(end_prompt)

            self.write("write memory"); await self.drain()
            await self.read_until_any(end_prompt)

            print(f"[OK] {self.port}: set {iface} {ip}")
        except Exception as e:
            print(f"[FAIL] {self.port}: {e}")

    def close(self):
        if self.writer:
            try:
                self.writer.close()
            except Exception:
                pass

async def main():
    conns = [TelnetConnection(HOST, p) for p in PORTS]
    try:
        await asyncio.gather(*(c.connect() for c in conns))
        await asyncio.gather(*(c.configure() for c in conns))
    finally:
        for c in conns:
            c.close()

if __name__ == "__main__":
    asyncio.run(main())
