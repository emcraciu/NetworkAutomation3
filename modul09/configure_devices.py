# connect to all devices in list
# call function to configure management interface
# close all connections

import asyncio

from lib.connectors.telnet_con import TelnetConnection

PORTS = [5073, 5072]
CONNS: list[TelnetConnection] = []
HOST = '92.81.55.146'

for port in PORTS:
    CONNS.append(
        TelnetConnection(HOST, port)
    )


async def main1():
    await asyncio.gather(*(con.connect() for con in CONNS))


async def main2():
    await asyncio.gather(*(con.configure() for con in CONNS))


asyncio.run(main1())
asyncio.run(main2())
