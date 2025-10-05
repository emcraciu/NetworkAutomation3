import asyncio
import re
import time
from multiprocessing import Queue

import telnetlib3

class TelnetConnection:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.reader=None
        self.writer=None

    def __enter__(self):
        return self

    async def connect(self):
        self.reader, self.writer = await telnetlib3.open_connection(self.host, self.port)
        self.write('')

    def print_info(self):
        print('Reader: {}'.format(self.reader))
        print('Writer: {}'.format(self.writer))

    async def readuntil(self, separator: str):
        response = await self.reader.readuntil(separator.encode())
        return response.decode()

    async def read(self, n: int):
        return await self.reader.read(n)
        # response = await self.reader.read(n)
        # return response.decode()

    def write(self, data: str):
        self.writer.write(data + '\r\n')

    async def enter_commands(self, command: list, prompt: str):
        for cmd in command:
            self.write(cmd)
            await self.readuntil(prompt)

    async def configure(self, completed: Queue = None):
       pass

    async def initialize_csr(self):
        self.write('')
        out= await self.readuntil('\n')
        print(out)
        print('Connecting to CSR')
        while 'dialog? [yes/no]:' not in out:
            self.writer.write('\n')
            time.sleep(3)
            out= await self.readuntil('\n')
            print('in loop')
        else:
            self.writer.write('n\n')
            time.sleep(1)
            out= await self.readuntil('\n')

        self.writer.write('\n')

        out = await self.read(n=1000)
        print(out)
        while 'Router>' not in out:
            self.write('')
            time.sleep(5)
            out = await self.read(n=1000)
            print(out)

        time.sleep(10)
        self.write('')
        out = await self.read(n=1000)
        return out

    async def enable_csr(self):
        self.write('')
        time.sleep(2)
        out= await self.read(n=100)
        if "CSR>" in out:
            self.writer.write('enable\n')
            while 'Password' not in out:
                self.writer.write('\n')
                time.sleep(1)
                out = await self.readuntil('\n')
            else:
                self.writer.write('Cisco123!\n')
                time.sleep(1)
                out= await self.readuntil('\n')
                #while '#' not in out:
                self.writer.write('\n')

        self.writer.write('')
        out= await self.read(n=100)
        return out

    async def ping_end_device(self, ping_ip: str) -> bool:
        self.write('')
        out= await self.readuntil('\n')
        self.write('ping ' + ping_ip + ' -c ' + '3')
        time.sleep(1)
        while 'packet loss, time' not in out:
            time.sleep(2)
            out = await self.readuntil('\n')
            print(out)
        if ' 0% packet loss' in out:
            return True
        else:
            return False

    async def get_response(self, command:str) -> str:
        self.write('')
        time.sleep(1)
        self.write(command)
        time.sleep(5)
        out = await self.read(n=1000)
        return out

    async def initialize_ftd(self, intf_obj, ftd_password: str):
        self.writer.write('\n')
        time.sleep(3)
        out = await self.read(n=1000)
        print(out)
        if out != '>':
            result=re.search(r'^\s*(?P<login>firepower login:)', out)
            print(result)
            if not result:
               return False

            while not result.group('login'):
                time.sleep(5)
            else:
                self.write('admin')
                await self.readuntil('Password:')
                time.sleep(2)
                self.write('Admin123')
                time.sleep(2)

            while not 'EULA:' in out:
                time.sleep(5)
                out = await self.read(n=1000)
            else:
                self.writer.write('\n')
                while True:
                    time.sleep(5)
                    out = await self.read(n=1000)
                    if '--More--' in out:
                        self.writer.write(' ')
                    elif 'EULA:' in out:
                        self.writer.write('\n')
                        time.sleep(5)
                        out = await self.read(n=1000)
                        break
                    else:
                        print('no str found in eula')

            while not 'password:' in out:
                time.sleep(5)
                out = await self.read(n=1000)
            else:
                self.writer.write(ftd_password +'\n')
                time.sleep(3)
                out = await self.read(n=1000)
                if 'password:' in out:
                    time.sleep(5)
                    self.writer.write(ftd_password + '\n')
                    time.sleep(3)
                    out = await self.read(n=1000)

            while not 'IPv4? (y/n) [y]:' in out:
                time.sleep(5)
                out = await self.read(n=1000)
            else:
                self.writer.write('\n')
                time.sleep(1)
                out = await self.read(n=1000)

            while not 'IPv6? (y/n) [n]:' in out:
                time.sleep(5)
                out = await self.read(n=1000)
            else:
                self.writer.write('\n')
                time.sleep(1)
                out = await self.read(n=1000)

            while not '[manual]:' in out:
                time.sleep(5)
                out = await self.read(n=1000)
            else:
                self.writer.write('\n')
                time.sleep(1)
                out = await self.read(n=1000)

            while not '[192.168.45.45]:' in out:
                time.sleep(5)
                out = await self.read(n=1000)
            else:
                self.writer.write(intf_obj.ipv4.ip.compressed + '\n')
                time.sleep(1)
                out = await self.read(n=1000)

            while not '[255.255.255.0]:' in out:
                time.sleep(5)
                out = await self.read(n=1000)
            else:
                self.writer.write(intf_obj.ipv4.netmask.exploded + '\n')
                time.sleep(1)
                out = await self.read(n=1000)

            while not '[192.168.45.1]:' in out:
                time.sleep(5)
                out = await self.read(n=1000)
                if 're-enter.' in out:
                    break
            else:
                self.writer.write((intf_obj.ipv4.network.network_address+1).compressed + '\n')
                time.sleep(1)
                out = await self.read(n=1000)

            while not '[firepower]:' in out:
                time.sleep(5)
                out = await self.read(n=1000)
            else:
                self.writer.write('\n')
                time.sleep(1)
                out = await self.read(n=1000)

            while not '::35]:' in out:
                time.sleep(5)
                out = await self.read(n=1000)
            else:
                self.writer.write('\n')
                time.sleep(1)
                out = await self.read(n=1000)

            while not "'none' []:" in out:
                time.sleep(5)
                out = await self.read(n=1000)
            else:
                self.writer.write('\n')
                time.sleep(1)
                out = await self.read(n=1000)

            while not "locally? (yes/no) [yes]:" in out:
                time.sleep(5)
                out = await self.read(n=1000)
            else:
                self.writer.write('\n')
                time.sleep(5)
                out = await self.read(n=1000)
            return True
        else:
            print("initial configuration already completed")
            return False


    def __exit__(self, exc_type, exc_val, exc_tb):
        self.write('\r\n')

if __name__ == '__main__':
    conn = TelnetConnection('92.81.55.146', 5052 )

    async def main():
        await conn.connect()
        conn.write('\n')
        await conn.enable_csr()
        conn.print_info()
    asyncio.run(main())
