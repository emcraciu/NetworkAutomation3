# ping devices when config is done
# Elvis
import asyncio
import os
from multiprocessing import Process, Queue
from lib.connectors.telnet_con import TelnetConnection
import subprocess

HOST = '92.81.55.146'
PORTS = [5072, 5073]

PORTS_IPS = [
    ("Ethernet0/0",        "192.168.200.2 255.255.255.0"),
    ("GigabitEthernet0/0", "192.168.200.3 255.255.255.0"),
]

CONNS: list[TelnetConnection] = []

for port in PORTS:
    CONNS.append(TelnetConnection(HOST, port))

async def configure_all(queue: Queue):
    await asyncio.gather(*(con.connect() for con in CONNS))
    await asyncio.gather(*(con.configure(completed=queue) for con in CONNS))
    # await asyncio.gather(*(con.close() for con in CONNS))

def ping_device(ip: str):
    print(f"{os.getpid()} Pinging {ip} ")
    subprocess.run(['ping', ip, '-c', '2'])

def consumer(queue: Queue):
    while not queue.empty():
        msg = queue.get()
        print("Got from queue:", msg)
        ip = next(msg.values().__iter__())
        ping_device(ip)
    print(f"Consumer {os.getpid()} done")


if __name__ == "__main__":
    q = Queue()
    asyncio.run(configure_all(q))
    p1 = Process(target=consumer, args=(q,))
    p1.start()
    p1.join()
