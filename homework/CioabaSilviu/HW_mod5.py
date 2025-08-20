import asyncio
import telnetlib3

HOST = "92.81.55.146"
PORT = 5186

class TelnetConn:
    def __init__(self, host, port):
        self.host, self.port = host, port
        self.reader = None
        self.writer = None

    async def connect(self):
        self.reader, self.writer = await telnetlib3.open_connection(self.host, self.port)
        await self._read_until_prompt()

    async def _read_until_prompt(self):
        buf = ""
        while True:
            chunk = await self.reader.read(256)
            if not chunk:
                break
            buf += chunk
            if buf.rstrip().endswith((">", "#")):
                break
        return buf

    async def cmd(self, c):
        self.writer.write(c.rstrip("\r\n") + "\n")
        await self.writer.drain()
        return await self._read_until_prompt()

    async def config(self, commands):
        await self.cmd("configure terminal")
        for c in commands:
            await self.cmd(c)
        await self.cmd("end")

    async def close(self):
        try:
            await self.cmd("write memory")
        except:
            pass
        self.writer.write("exit\n")
        await self.writer.drain()


async def main():
    conn = TelnetConn(HOST, PORT)
    await conn.connect()
    await conn.cmd("terminal length 0")


    iface_cmds = [
        "interface e0/0",
        "ip address 192.168.1.1 255.255.255.0",
        "no shutdown",
        "exit",
        "interface e0/1",
        "ip address 192.168.10.1 255.255.255.0",
        "no shutdown",
        "exit",
        "interface e0/2",
        "ip address 192.168.0.1 255.255.255.0",
        "no shutdown",
        "exit",
    ]
    await conn.config(iface_cmds)

    dhcp_cmds = [
        "ip dhcp excluded-address 192.168.10.1",
        "ip dhcp pool POOL1",
        "network 192.168.10.0 255.255.255.0",
        "default-router 192.168.10.1",
        "dns-server 8.8.8.8 1.1.1.1",
        "exit",
    ]
    await conn.config(dhcp_cmds)


    ssh_cmds = [
        "hostname IOU"
        "ip domain-name savnet.ro",
        "ip ssh version 2",
        "username cisco secret cisco",
        "crypto key generate rsa modulus 2048",
        "line vty 0 4",
        "transport input ssh",
        "login local",
        "exit",
        "service password-encryption",
    ]
    await conn.config(ssh_cmds)


    print(await conn.cmd("show ip interface brief"))
    print(await conn.cmd("show ip dhcp binding"))
    print(await conn.cmd("show ip ssh"))

    await conn.close()

if __name__ == "__main__":
    asyncio.run(main())
