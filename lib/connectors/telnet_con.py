import asyncio

import telnetlib3

HOST = '92.81.55.146'
PORT = 5041  # replace with yours

class TelnetConnection:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        asyncio.run(self.connect_to_device())


    async def connect_to_device(self):
        self.reader, self.writer = await telnetlib3.open_connection(self.host, self.port)

    def print_info(self):
        print('Reader: {}'.format(self.reader))
        print('Writer: {}'.format(self.writer))

    async def readuntil(self, separator: str):
        return await self.reader.readuntil(separator.encode())

    async def read(self, n: int):
        return await self.reader.read(n)

    def write(self, data: str):
        self.writer.write(data)

if __name__ == '__main__':
    conn = TelnetConnection(HOST, PORT)
    conn.print_info()