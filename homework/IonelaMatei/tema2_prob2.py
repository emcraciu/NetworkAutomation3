'''
# Use connection classes

1) Based on the code in '[telnet_con.py](../lib/connectors/telnet_con.py)' add support for
   configuring CSR router with initial configuration:
   - add IP addresses for all interfaces of IOU1 device
   - enable DHCP server on ethernet 0/1
   - enable ssh and set user / pass for ssh access
'''
import asyncio
from lib.connectors.telnet_con import TelnetConnection
HOST = '92.81.55.146'
PORT = 5109

async def initial_setup(conn: TelnetConnection):
    commands = [
        "configure terminal",
        "interface e0/0",
        " ip address 192.168.1.1 255.255.255.0",
        " no shutdown",
        "exit",
        "interface e0/1",
        " ip address 192.168.2.1 255.255.255.0",
        " no shutdown",
        "exit",
        "ip dhcp pool LAN",
        " network 192.168.2.0 255.255.255.0",
        " default-router 192.168.2.1",
        "exit",
        "ip domain name cisco.com",
        "crypto key generate rsa ",
        "2048",
        "exit",
        "ip ssh version 2",
        "username admin privilege 15 secret admin123",
        "line vty 0 4",
        " login local",
        " transport input ssh",
        "end",
        "write memory"
    ]

    for command in commands:
        conn.write(command + "\n")
        await asyncio.sleep(0.2)


async def run_setup():
    conn = TelnetConnection(HOST, PORT)
    await conn.connect_to_device()
    conn.write("\n")
    await conn.readuntil("IOU1#")
    await initial_setup(conn)
print("Configuratie realizata !")

asyncio.run(run_setup())