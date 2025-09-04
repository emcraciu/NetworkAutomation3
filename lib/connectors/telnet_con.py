import asyncio
from os import write
from queue import Queue

import telnetlib3

HOST = '92.81.55.146'
PORT = 5072  # replace with yours

class TelnetConnection:
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def __enter__(self):
        return self

    async def connect(self):
        self.reader, self.writer = await telnetlib3.open_connection(self.host, self.port)

    def print_info(self):
        print('Reader: {}'.format(self.reader))
        print('Writer: {}'.format(self.writer))

    async def readuntil(self, separator: str):
        response = await self.reader.readuntil(separator.encode())
        return response.decode()

    async def read(self, n: int):
        return await self.reader.read(n)

    def write(self, data: str):
        self.writer.write(data + '\r\n')

    async def execute_commends(self, command: list, prompt: str):
        for cmd in command:
            self.write(cmd)
            await self.readuntil(prompt)

    async def configure(self, completed: Queue = None):
        self.write('')
        await asyncio.sleep(2)
        result = await self.read(3000)
        if 'Router#' in result:
            self.write('conf t')
            await self.readuntil('Router(config)#')
            self.write('interface g0/0')
            await self.readuntil('Router(config-if)#')
            self.write('ip address 192.168.200.3 255.255.255.0')
            await self.readuntil('Router(config-if)#')
            self.write('no shutdown')
            await self.readuntil('Router(config-if)#')
            completed.put({"Router": "192.168.200.3"})

        elif 'IOU1#' in result:
            self.write('conf t')

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.write('\r\n')

if __name__ == '__main__':
    conn = TelnetConnection(HOST, PORT)

    async def main():
        await conn.connect()
        conn.write('\n')
        await conn.readuntil('\n')
        conn.print_info()
    asyncio.run(main())
