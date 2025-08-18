import asyncio
import time

from lib.connectors.telnet_con import TelnetConnection


class Interface:
    def __init__(self, connection, name):
        self.connection = connection
        self.name = name

    def clean(self):
        self.connection.write(f'end\nconf t\nint {self.name}\n')

    def add_ip(self, ip, mask):
        self.clean()
        self.connection.write(f'ip add {ip} {mask}\n')

    def no_shut_interface(self):
        self.clean()
        self.connection.write(f'no shut\n')

    async def get_ip(self):
        self.clean()
        self.connection.write(f'do show ip int br | include {self.name}\n')
        time.sleep(1)
        response = await asyncio.wait_for(self.connection.read(1000), timeout=5)
        for line in response.splitlines():
            if 'YES' in line:
                self.ip = line.split()[1]

    async def add_dhcp_pool_for_interface(self, interface):
        self.clean()
        await self.get_ip()
        self.connection.write(f'ip dhcp pool {self.interfaces[interface]}\n'
                              f'network 192.168.1.0 255.255.255.0\n'
                              f'default-router 192.168.1.1\n')

class Router:
    def __init__(self, host, port):
        self.connection = TelnetConnection(host, port)
        self.interfaces = {}

    async def connect_to_router(self):
        await self.connection.connect_to_device()
        self.connection.print_info()

    def clean(self):
        self.connection.write(f'end\nconf t\n')

    def add_interface(self, name):
        self.interfaces[name] = Interface(self.connection, name)




async def main():
    host = '92.81.55.146'
    port = 5047

    router = Router(host, port)
    await router.connect_to_router()

    # router.add_interface('Ethernet0/0')
    # router.interfaces['Ethernet0/0'].add_ip('192.168.0.1', '255.255.255.0')
    # router.interfaces['Ethernet0/0'].no_shut_interface()
    #
    router.add_interface('Ethernet0/1')
    router.interfaces['Ethernet0/1'].add_ip('192.168.1.1', '255.255.255.0')
    router.interfaces['Ethernet0/1'].no_shut_interface()
    #
    # router.add_interface('Ethernet0/2')
    # router.interfaces['Ethernet0/2'].add_ip('192.168.2.1', '255.255.255.0')
    # router.interfaces['Ethernet0/2'].no_shut_interface()

    await router.interfaces['Ethernet0/1'].get_ip()

if __name__ == '__main__':
    asyncio.run(main())