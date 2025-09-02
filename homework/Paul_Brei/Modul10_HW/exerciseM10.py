import asyncio
import time

from lib.connectors.telnet_con import TelnetConnection

HOST = '92.81.55.146'
PORT = 5113
command = 'show running-config'

class ParseConfig:
    def __init__(self, conn, hostname, read_limit=1000):
        self.conn = conn
        self.hostname = hostname
        self.read_limit = read_limit

    def clean_lines(self, lines: str):
        return '\n'.join(
            line for line in lines.splitlines()
            if '--More--' not in line
            and '\x08' not in line
            and command not in line
            and self.hostname not in line
        ) + '\n'

    async def save_running_config(self, file_name:str):
        with open(file_name, "w+") as file:
            await self.conn.connect()
            self.conn.write('')
            response = await self.conn.readuntil(self.hostname)
            if self.hostname in response:
                self.conn.writer.write(command + '\n')
                file.write(self.clean_lines(response))
                await asyncio.sleep(0.5)
                partial = await asyncio.wait_for(self.conn.reader.read(self.read_limit), timeout=2)
                print(partial)
                while "--More--" in partial:
                    lines = self.clean_lines(partial)
                    file.write(lines)
                    self.conn.writer.write(' ')
                    time.sleep(0.5)
                    partial = await asyncio.wait_for(self.conn.reader.read(self.read_limit), timeout=2)
                else:
                    file.write(self.clean_lines(partial))

        file.close()

    async def reload_device(self):
        self.conn.write('')
        await self.conn.readuntil(self.hostname)
        self.conn.write('reload')
        await self.conn.readuntil("Save?")
        self.conn.write('n')
        await self.conn.readuntil("Proceed with reload?")
        self.conn.write('')
        await self.conn.readuntil("crypto-engine")
        self.conn.write('\n')

    def get_config_block(self, file_name:str, words:str):
        with open(file_name, "r") as file:
            res_str=''
            file.seek(0)
            content = file.read()
            blocks=content.split('!\n')
            for block in blocks:
                if block.startswith(words):
                    block_lines=block.splitlines()
                    for line in range(1, len(block_lines)):
                        res_str+=block_lines[line].strip()+'\\n'

                    return res_str
            return None

async def main():
    connection = TelnetConnection(HOST, PORT)
    parser1 = ParseConfig(connection, "IOU1#", 5000)

    await parser1.save_running_config("IOU_initial_running_config.txt")
    initial_config_content = parser1.get_config_block(
        "IOU_initial_running_config.txt",
        "interface Ethernet0/3"
    )
    await parser1.reload_device()

    print("initial config:", initial_config_content)

    await asyncio.sleep(20)  # tweak depending on your device boot time

    # Try reconnecting until success
    while True:
        try:
            connection2 = TelnetConnection(HOST, PORT)
            parser2 = ParseConfig(connection2, "IOU1#", 5000)
            await parser2.save_running_config("IOU_new_running_config.txt")
            break
        except Exception as e:
            print("Device not ready yet, retrying in 10s:", e)
            await asyncio.sleep(10)


if __name__ == "__main__":
    asyncio.run(main())