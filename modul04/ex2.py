# get full configuration (running/startup config) from IOU1 and save to file
import asyncio
import time

import telnetlib3

HOST = '92.81.55.146'
PORT = 5041  # replace with yours
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


async def connect_to_device(host, port):
    reader, writer = await telnetlib3.open_connection(host, port)
    writer.write('\n')
    response = await reader.readuntil(b"IOU1#")
    if "IOU1#" in response.decode():
        with open("running_config.txt", "w") as file:
            writer.write(command + '\n')
            file.write(clean_lines(response.decode()))
            time.sleep(0.5)
            partial = await asyncio.wait_for(reader.read(1000), timeout=2)
            while "--More--" in partial:
                lines = clean_lines(partial)
                file.write(lines)
                writer.write(' ')
                time.sleep(0.5)
                partial = await asyncio.wait_for(reader.read(1000), timeout=2)
            else:
                file.write(clean_lines(partial))


asyncio.run(connect_to_device(HOST, PORT))
