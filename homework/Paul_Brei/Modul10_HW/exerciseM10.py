import asyncio
import time

from lib.connectors.telnet_con import TelnetConnection

HOST = '92.81.55.146'
PORT_IOU = 5113
PORT_IOSv = 5115
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
            and f'{self.hostname}#' not in line
        ) + '\n'

    async def configure_ssh(self,interface:str, ip:str, mask:str):
        await self.conn.connect()
        self.conn.write('')
        await self.conn.readuntil(f'{self.hostname}#')
        self.conn.write('conf t')
        await self.conn.readuntil(f'{self.hostname}(config)#')
        self.conn.write("username user password pass")
        self.conn.write(f"hostname {self.hostname}")
        self.conn.write("ip domain name savnet.ro")
        self.conn.write("crypto key generate rsa modulus 2048")
        await asyncio.sleep(2)
        await self.conn.readuntil(f'{self.hostname}(config)#')
        self.conn.write("enable secret pass")
        await asyncio.sleep(2)
        await self.conn.readuntil(f'{self.hostname}(config)#')
        self.conn.write("line vty 0 4")
        await self.conn.readuntil(f'{self.hostname}(config-line)#')
        self.conn.write("transport input ssh")
        self.conn.write("login local")
        self.conn.write("exit")
        await self.conn.readuntil(f'{self.hostname}(config)#')
        self.conn.write(f"int {interface}")
        await self.conn.readuntil(f'{self.hostname}(config-if)#')
        self.conn.write(f"ip address {ip} {mask}")
        self.conn.write("no sh")
        await asyncio.sleep(2)
        self.conn.write("end")


    async def save_running_config(self, file_name:str):
        with open(file_name, "w+") as file:
            await self.conn.connect()
            self.conn.write('')
            response = await self.conn.readuntil(f'{self.hostname}#')
            if f'{self.hostname}#' in response:
                await asyncio.sleep(2)
                self.conn.writer.write(command + '\n')
                file.write(self.clean_lines(response))
                await asyncio.sleep(2)
                partial = await asyncio.wait_for(self.conn.reader.read(self.read_limit), timeout=2)
                #print(partial)
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
        await self.conn.readuntil(f'{self.hostname}#')
        self.conn.write('reload')
        await self.conn.readuntil("Save?")
        self.conn.write('n')
        await self.conn.readuntil("Proceed with reload?")
        self.conn.write('')
        await self.conn.readuntil("crypto-engine")
        self.conn.write('\n')

    async def start_device(self):
        await self.conn.connect()
        self.conn.write('\n')

    async def modify_config_block(self, block:str):
        lines=block.split('\n ')
        interface_name=lines[0]
        self.conn.write('')
        await self.conn.readuntil(f'{self.hostname}#')
        self.conn.write("conf t")
        await self.conn.readuntil(f'{self.hostname}(config)#')
        self.conn.write(f"{interface_name}")
        for line in lines[1:]:
            self.conn.write(line)

        await asyncio.sleep(1)
        self.conn.write("end")

def compare_files(f_name1:str, f_name2:str):
    changed_blocks=[]
    blocks1=set()
    blocks2=set()
    with open(f_name1, "r") as file1:
        content1 = file1.read()
    with open(f_name2, "r") as file2:
        content2 = file2.read()

    raw_blocks1 = [block.strip() for block in content1.split('!\n') if block.strip()]
    raw_blocks2 = [block.strip() for block in content2.split('!\n') if block.strip()]

    blocks1 = set(block for block in raw_blocks1 if block.startswith("interface") or block.startswith("line vty 0 4"))
    blocks2 = set(block for block in raw_blocks2 if block.startswith("interface") or block.startswith("line vty 0 4"))

    #changed_blocks = list(blocks1.symmetric_difference(blocks2))

    for block1 in blocks1:
        if block1 not in blocks2 and "no ip address" not in block1:
            changed_blocks.append(block1)

    return changed_blocks

async def main():
    connection_IOU = TelnetConnection(HOST, PORT_IOU)
    parser1 = ParseConfig(connection_IOU, "IOU1", 5000)

    await parser1.configure_ssh('e0/2','192.168.200.2','255.255.255.0')
    await parser1.save_running_config("IOU_initial_running_config.txt")
    await parser1.reload_device()

    await asyncio.sleep(5)

    # connection_IOSv = TelnetConnection(HOST, PORT_IOSv)
    # parserIOSv1 = ParseConfig(connection_IOSv, "Router", 5000)
    #
    # await parserIOSv1.configure_ssh('g0/1','192.168.200.3','255.255.255.0')
    # await parserIOSv1.save_running_config("IOSv_initial_running_config.txt")
    # await parserIOSv1.reload_device()
    #
    # await asyncio.sleep(5)

    while True:
        try:
            connection_IOU2 = TelnetConnection(HOST, PORT_IOU)
            parser2 = ParseConfig(connection_IOU2, "IOU1", 5000)
            await parser2.start_device()
            await parser2.save_running_config("IOU_new_running_config.txt")
            break
        except Exception as e:
            await asyncio.sleep(5)

    # while True:
    #     try:
    #         connection_IOSv2 = TelnetConnection(HOST, PORT_IOSv)
    #         parserIOSv2 = ParseConfig(connection_IOSv2, "Router", 5000)
    #         await parserIOSv2.start_device()
    #         await parserIOSv2.save_running_config("IOSv_new_running_config.txt")
    #         break
    #     except Exception as e:
    #         await asyncio.sleep(5)

    blocks_IOU=compare_files("IOU_initial_running_config.txt", "IOU_new_running_config.txt")
    for block in blocks_IOU:
        await parser2.modify_config_block(block)

    print("changed blocks IOU:\n",blocks_IOU)

    # blocks_IOSv=compare_files("IOSv_initial_running_config.txt", "IOSv_new_running_config.txt")
    # for block in blocks_IOSv:
    #     await parserIOSv2.modify_config_block(block)
    #
    # print("changed blocks IOSv:\n",blocks_IOSv)

if __name__ == "__main__":
    asyncio.run(main())
