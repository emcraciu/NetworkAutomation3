import asyncio
import telnetlib3

HOST = "92.81.55.146"
PORT = 5079  # portul Telnet spre consola routerului din GNS3

IFACES = [
    ("e0/1", "192.168.1.10", "255.255.255.0"),
    ("e0/2", "192.168.1.11", "255.255.255.0"),
]

async def send(writer, cmd: str):
    writer.write(cmd + "\r\n")
    await writer.drain()

async def expect(reader, mark, timeout: float = 6.0) -> str:
    # telnetlib3.readuntil are nevoie de bytes în setup-ul tău
    if isinstance(mark, str):
        mark = mark.encode()
    data = await asyncio.wait_for(reader.readuntil(mark), timeout=timeout)
    # întoarce text pentru ușurință
    return data.decode(errors="ignore")

async def configure_all():
    reader, writer = await telnetlib3.open_connection(HOST, PORT)
    try:
        # Aduce promptul
        await send(writer, "")
        buf = ""
        try:
            buf = await expect(reader, ">")
        except asyncio.TimeoutError:
            buf = await expect(reader, "#")

        # Intră în enable dacă e în exec
        if ">" in buf:
            await send(writer, "enable")
            await expect(reader, "#")

        # Previne paginația
        await send(writer, "terminal length 0")
        await expect(reader, "#")

        # Intră în config
        await send(writer, "conf t")
        await expect(reader, "(config)#")

        # Configurează toate interfețele secvențial
        for iface, ip, mask in IFACES:
            await send(writer, f"interface {iface}")
            await expect(reader, "(config-if)")
            await send(writer, f"ip address {ip} {mask}")
            await expect(reader, "(config-if)")
            await send(writer, "no shutdown")
            await expect(reader, "(config-if)")
            await send(writer, "exit")
            await expect(reader, "(config)#")
            print(f"[OK] {iface} -> {ip} {mask}")

        # Revino și salvează
        await send(writer, "end")
        await expect(reader, "#")
        await send(writer, "write memory")  # sau 'copy running-config startup-config'
        try:
            await expect(reader, "#")
        except asyncio.TimeoutError:
            await send(writer, "")
            await expect(reader, "#")

        print("[DONE] Config saved.")
    finally:
        writer.close()
        try:
            await writer.wait_closed()
        except Exception:
            pass

async def main():
    await configure_all()

if __name__ == "__main__":
    asyncio.run(main())

# Andrei Rad
import threading
import asyncio
from lib.connectors.telnet_con import TelnetConnection

HOST = "92.81.55.146"
PORT = 5072
lock = threading.Lock()


async def config_int(interface: str, ip: str, ) -> None:
    conn = TelnetConnection(HOST, PORT)
    await conn.connect()

    conn.write('\n')
    await conn.readuntil('#')
    conn.write('conf t\n')
    await conn.readuntil('(config)#')
    conn.write(f'int {interface}\n')
    await conn.readuntil('(config-if)#')
    conn.write(f'ip add {ip} 255.255.255.0\n')
    await conn.readuntil('(config-if)#')
    conn.write('no sh\n')
    await conn.readuntil('(config-if)#')
    conn.write('end\n')
    await conn.readuntil('#')


def config_threads(interface, ip):
    with lock:
        asyncio.run(config_int(interface, ip))


t1 = threading.Thread(target=config_threads, args=('e0/1', '192.168.201.1'))
t2 = threading.Thread(target=config_threads, args=('e0/2', '192.168.202.1'))
t1.start()
t2.start()
t1.join()
t2.join()


# Silviu
import asyncio, threading, telnetlib3

HOST, PORT = "92.81.55.146", 5072
IFACES = {
    "e0/1": "192.168.201.4 255.255.255.0",
    "e0/2": "192.168.202.5 255.255.255.0"
}
CMDS = ["", "conf t", "int {iface}", "ip address {ip}", "no shut", "end", "wr"]


async def configure(iface, ip):
    r, w = await telnetlib3.open_connection(HOST, PORT)

    def send(cmd):
        w.write(cmd + "\r\n")

    async def wait():
        await r.readuntil(b"#")

    cmds = list(map(lambda x: x.format(iface=iface, ip=ip), CMDS))
    for cmd in cmds:
        send(cmd)
        await wait()
    print(f"[OK] {iface} -> {ip}")
    w.close()


def thr(iface, ip):
    asyncio.run(configure(iface, ip))


# threads = [threading.Thread(target=thr, args=(i, ip)) for i, ip in IFACES.items()]
# [t.start() for t in threads]
# [t.join() for t in threads]
