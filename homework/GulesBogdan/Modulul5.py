import asyncio

import telnetlib3

HOST = '92.81.55.146'
PORT = 5168  # replace with yours

configuration = [
    'conf t',
    'interface Ethernet0/0',
    'ip address 172.16.1.1 255.255.255.0',
    'no shutdown',
    'exit',
    'interface Ethernet0/1',
    'ip address 172.16.2.1 255.255.255.0',
    'no shutdown',
    'exit',
    'interface Ethernet0/2',
    'ip address 172.16.3.1 255.255.255.0',
    'no shutdown',
    'exit',

    # DHCP
    'ip dhcp excluded-address 172.16.2.2 172.16.2.10',
    'ip dhcp pool IOU1_DHCP',
    'network 172.16.2.0 255.255.255.0',
    'default-router 172.16.2.1',
    'exit',

    # SSH
    'ip domain-name cisco.com',
    'crypto key generate rsa modulus 1024',
    'ip ssh version 2',
    'username cisco secret cisco',
    'line vty 0 15',
    'login local',
    'transport input ssh',
    'exit',

    'end',
    'write memory'



]

class TelnetConnection:
    def __init__(self, host, port):
        self.host = host
        self.port = port

    async def connect_to_device(self):
        self.reader, self.writer = await telnetlib3.open_connection(self.host, self.port)

    async def run(self, rows):
        for i in rows:
            self.writer.write(i+'\n')
            await asyncio.sleep(1)

    async def close(self):
        self.writer.write("exit\n")
        await asyncio.sleep(1)
        self.writer.close()
        await self.writer.wait_closed()

async def main():
    conn=TelnetConnection(HOST, PORT)
    await conn.connect_to_device()
    await conn.run(configuration)
    await conn.close()

if __name__ == '__main__':
    asyncio.run(main())