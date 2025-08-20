import asyncio

import telnetlib3

HOST = '92.81.55.146'
PORT = 5047  # replace with yours

class TelnetConnection:
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def __enter__(self):
        return self

    async def connect_to_device(self):
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
        self.writer.write(data)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.write('\n')

if __name__ == '__main__':
    pass
    # conn = TelnetConnection(HOST, PORT)
    # asyncio.run(conn.connect_to_device())
    # conn.print_info()

    # with TelnetConnection(HOST, PORT) as conn:
    #     asyncio.run(conn.connect_to_device())
    #     conn.print_info()