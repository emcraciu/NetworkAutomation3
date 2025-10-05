import asyncio
import time

from lib.connectors.telnet_con import TelnetConnection

class ParseConfig:
    def __init__(self, conn, read_limit=1000):
        self.conn = conn
        self.read_limit = read_limit
        self.file=None
        self.file_name="running-config.txt"

    def __enter__(self):
        self.file=open(self.file_name, "w+")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.file.close()
        return False

    @staticmethod
    def clean_lines(lines: str):
        return '\n'.join(
            line for line in lines.splitlines()
            if '--More--' not in line
            and '\x08' not in line
            and command not in line
            and hostname not in line
        ) + '\n'

    async def connect_to_device(self):
        await self.conn.connect_to_device()
        self.conn.write('\n')
        response = await self.conn.readuntil("IOU1#")
        if "IOU1#" in response:
            self.conn.write(command + '\n')
            self.file.write(self.clean_lines(response))
            time.sleep(0.5)
            partial = await asyncio.wait_for(self.conn.read(self.read_limit), timeout=2)
            while "--More--" in partial:
                lines = self.clean_lines(partial)
                self.file.write(lines)
                self.conn.write(' ')
                time.sleep(0.5)
                partial = await asyncio.wait_for(self.conn.read(self.read_limit), timeout=2)
            else:
                self.file.write(self.clean_lines(partial))

    def get_config_block(self, words:str):
        res_str=''
        self.file.seek(0)
        content = self.file.read()
        blocks=content.split('!\n')
        for block in blocks:
            if block.startswith(words):
                block_lines=block.splitlines()
                for line in range(1, len(block_lines)):
                    res_str+=block_lines[line].strip()+'\\n'

                return res_str
        return None

HOST = '92.81.55.146'
PORT = 5113
command = 'show running-config'
hostname = "IOU1#"

connection = TelnetConnection(HOST, PORT)

with ParseConfig(connection, 5000) as parser:
    asyncio.run(parser.connect_to_device())
    config_content = parser.get_config_block("interface Ethernet0/3")

print(config_content)