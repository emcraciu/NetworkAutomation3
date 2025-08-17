# get full configuration (running/startup config) from IOU1 and save to file
import asyncio
import time

import telnetlib3

from lib.connectors.telnet_con import TelnetConnection

HOST = '92.81.55.146'
PORT = 5102  # replace with yours
command = 'show running-config'
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
    response = await conn.readuntil("IOU1#")
    if "IOU1#" in response:
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


asyncio.run(connect_to_device())
