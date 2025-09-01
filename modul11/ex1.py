# configure in different threads different interfaces on same IOU1 device

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
    "e0/1": "192.168.200.4 255.255.255.0",
    "e0/2": "192.168.200.5 255.255.255.0"
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


threads = [threading.Thread(target=thr, args=(i, ip)) for i, ip in IFACES.items()]
[t.start() for t in threads]
[t.join() for t in threads]
