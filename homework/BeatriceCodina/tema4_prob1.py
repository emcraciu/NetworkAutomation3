'''
# Loading initial configuration form file

## Initial router configuration needs to be loaded from a file like the one we have saved.

- create configuration manually on IOU and IOSv that will include:
  - interface IP address
  - creating user and password
  - set hostname
  - allow ssh access
  - enable password (optional)
  - enable restconf (optinal)

- save the configuration of the IOU and IOSv to a file
- modify some changes or revert the device to factory settings (optional create method to rest to factory and call it)
- get current configuration of the device and compare it to the saved configuration
- extract the configuration blocks that need to be modified
- execute only the required lines to bring the device back to the configuration done manually
'''


import asyncio
from telnet_conn_tema4 import TelnetConnection
import os

PORTS = [5120, 5121]
HOST = '92.81.55.146'
print(os.getcwd())
CONNS = [TelnetConnection(HOST, port) for port in PORTS]

PORT_FILE_MAP = {
    5120: ("IOU1_initial.txt", "IOU1_current.txt"),
    5121: ("CiscoIOSv_initial.txt", "CiscoIOSv_current.txt")
}
def compare_configs(initial_file, current_file):
    with open(initial_file) as f:
        initialline = f.readlines()
    with open(current_file) as f:
        current = f.readlines()
    changed = False
    for i in range(max(len(initialline), len(current))):
        initial = initialline[i].strip() if i < len(initialline) else ""
        curr = current[i].strip() if i < len(current) else ""
        if initial != curr:
            changed = True
            print(f"Line {i+1}:")
            print(f"   Inital: {initial}")
            print(f"   Current : {curr}")

    if not changed:
        print(f"Nu exista diferente in {initial_file}")


async def main():
    await asyncio.gather(*(con.connect() for con in CONNS))
    for con in CONNS:
        files = PORT_FILE_MAP[con.port]
        initial_file = files[0]
        current_file = files[1]
        await con.configure(filename=initial_file)

    await asyncio.gather(*(con.close() for con in CONNS))

    input("\nModificați configurația device-urilor în GNS3 și apăsați Enter...")

    await asyncio.gather(*(con.connect() for con in CONNS))

    for con in CONNS:
        files = PORT_FILE_MAP[con.port]
        initial_file = files[0]
        current_file = files[1]
        await con.configure(filename=current_file)

    await asyncio.gather(*(con.close() for con in CONNS))

    for port, files in PORT_FILE_MAP.items():
        initial_file = files[0]
        current_file = files[1]
        print(f"\nComparare {initial_file} cu {current_file}:")
        compare_configs(initial_file, current_file)

    for con in CONNS:
        files = PORT_FILE_MAP[con.port]
        initial_file = files[0]
        current_file = files[1]

        with open(initial_file) as f_init, open(current_file) as f_curr:
            init_lines = f_init.readlines()
            curr_lines = f_curr.readlines()
            commands_to_restore = []
            for i in range(max(len(init_lines), len(curr_lines))):
                init = init_lines[i].strip() if i < len(init_lines) else ""
                curr = curr_lines[i].strip() if i < len(curr_lines) else ""
                if init != curr and init != "":
                    commands_to_restore.append(init)

        if commands_to_restore:
            await con.connect()
            await con.restore_config(commands_to_restore)
            await con.close()

asyncio.run(main())