from typing import Optional
import telnetlib3


class TelnetConnection:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.reader: Optional[telnetlib3.TelnetReader] = None
        self.writer: Optional[telnetlib3.TelnetWriter] = None

    async def connect(self):
        self.reader, self.writer= await telnetlib3.open_connection(self.host, self.port)

    async def read_until(self, separator: str):
        return (await self.reader.readuntil(separator.encode())).decode()

    async def read(self, n: int):
        return await self.reader.read(n)

    async def execute_commands(self, command: list, prompt: str):
        for cmd in command:
            self.write(cmd+'\n')
            await self.read_until(prompt)

    def write(self, data: str):
        self.writer.write(data)

    def close(self):
        self.writer.close()
