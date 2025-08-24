import asyncio
import time

import telnetlib3

from lib.connectors.telnet_con import TelnetConnection

HOST = '92.81.55.146'
PORT = 5104  # replace with yours
command = 'configure terminal'
interfaces = ["e0/0", "e0/1", "e0/2"]
hostname = "IOU1#"


def clean_lines(lines: str):
    return '\n'.join(
        line for line in lines.splitlines()
        if '--More--' not in line
        and '\x08' not in line
        and command not in line
        and hostname not in line
    ) + '\n'


conn = TelnetConnection(HOST, PORT)


async def connect_to_device():
    await conn.connect_to_device()
    conn.write('\n')
    response = await conn.readuntil(hostname)
    if hostname in response:
        with open("running_config.txt", "w") as file:
            conn.write(command + '\n')
            file.write(clean_lines(response))
            time.sleep(0.5)
            partial = await asyncio.wait_for(conn.read(1000), timeout=2)
            while "--More--" in partial:
                lines = clean_lines(partial)
                file.write(lines)
                conn.write(' ')
                time.sleep(0.5)
                partial = await asyncio.wait_for(conn.read(1000), timeout=2)
            else:
                file.write(clean_lines(partial))
            for idx, intf in enumerate(interfaces, 0):
                ip = 1 + idx * 4
                conn.write(f"int {intf}" + '\n')
                conn.write(f"ip address 192.168.1.{ip} 255.255.255.252" + '\n')
                conn.write("no shutdown" + '\n')
                file.write(clean_lines(response))
                time.sleep(0.5)
            conn.write("do wr" + '\n')
            file.write(clean_lines(response))
            time.sleep(0.5)


asyncio.run(connect_to_device())
