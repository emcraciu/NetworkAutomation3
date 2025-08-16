import asyncio

import telnetlib3

HOST = '92.81.55.146'
PORT = 5052  # replace with yours
command = 'show running-config'
hostname = "IOU1#"

class TelnetConnection:
    def __init__(self, host, port):
        self.host = host
        self.port = port

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

    async def set_interface_ips(self, port_ip_dict: dict):
        self.write("conf t\n")
        await self.readuntil("(config)#")
        for port, ip in port_ip_dict.items():
            self.write(f"int {port}\n")
            await self.readuntil("(config-if)#")
            self.write(f"ip address {ip}\n")
            await self.readuntil("(config-if)#")
            self.write("no sh\n")
            await self.readuntil("(config-if)#")
            self.write("exit\n")
            await self.readuntil("(config)#")

        self.write("end\n")
        await self.readuntil("#")

    async def enable_dhcp(
            self,
            pool_name: str = "LAN20",
            network: str = "192.168.20.0 255.255.255.0",
            default_router: str = "192.168.20.1",
            dns_server: str = "8.8.8.8",
            excluded: str = "192.168.20.1 192.168.20.20",
            domain_name: str = "savnet.ro"
    ):
        self.write("conf t\n")
        await self.readuntil("(config)#")
        if excluded:
            self.write(f"ip dhcp excluded-address {excluded}\n")
            await self.readuntil("(config)#")
        if domain_name:
            self.write(f"ip domain name {domain_name}\n")
            await self.readuntil("(config)#")

        self.write(f"ip dhcp pool {pool_name}\n")
        await self.readuntil("(dhcp-config)#")
        self.write(f"network {network}\n")
        await self.readuntil("(dhcp-config)#")
        self.write(f"default-router {default_router}\n")
        await self.readuntil("(dhcp-config)#")

        if dns_server:
            self.write(f"dns-server {dns_server}\n")

        self.write("exit\n")
        await self.readuntil("(config)#")

        self.write("end\n")
        await self.readuntil("#")

    async def enable_ssh(
            self,
            local_user: str = "cisco",
            local_secret: str = "cisco",
            hostname_device: str = "IOU1",
            domain_name: str = "savnet.ro",
            rsa_bits: int = 2048
    ):
        self.write("conf t\n")
        await self.readuntil("(config)#")

        self.write(f"hostname {hostname_device}\n")
        await self.readuntil("(config)#")
        self.write(f"ip domain name {domain_name}\n")
        await self.readuntil("(config)#")

        self.write(f"username {local_user} privilege 15 secret {local_secret}\n")
        await self.readuntil("(config)#")
        self.write(f"enable secret {local_secret}\n")
        await self.readuntil("(config)#")

        self.write("line vty 0 4\n")
        await self.readuntil("(config-line)#")
        self.write("transport input ssh\n")
        await self.readuntil("(config-line)#")
        self.write("login local\n")
        await self.readuntil("(config-line)#")

        self.write("exit\n")
        await self.readuntil("(config)#")

        self.write("end\n")
        await self.readuntil("#")

        self.write(f"crypto key generate rsa modulus {rsa_bits}\n")
        await self.readuntil("#")

conn = TelnetConnection(HOST, PORT)

async def connect_to_device_and_set_ip():
    await conn.connect_to_device()
    conn.write('\n')
    response = await conn.readuntil(hostname)

    if hostname in response:
        port_ip_dict = {
            "Ethernet0/0": "192.168.10.1 255.255.255.0",
            "Ethernet0/1": "192.168.20.1 255.255.255.0",
        }
        await conn.set_interface_ips(port_ip_dict)

async def connect_to_device_and_enable_dhcp():
    await conn.connect_to_device()
    conn.write('\n')
    response = await conn.readuntil(hostname)

    if hostname in response:
        await conn.enable_dhcp(
            pool_name="LAN20",
            network="192.168.20.0 255.255.255.0",
            default_router="192.168.20.1",
            dns_server="8.8.8.8",
            excluded="192.168.20.1 192.168.20.20",
            domain_name="savnet.ro"
        )

async def connect_to_device_and_enable_ssh():
    await conn.connect_to_device()
    conn.write('\n')
    response = await conn.readuntil(hostname)

    if hostname in response:
        await conn.enable_ssh(
            local_user="cisco",
            local_secret="cisco",
            hostname_device="IOU1",
            domain_name="savnet.ro",
            rsa_bits=2048
        )

asyncio.run(connect_to_device_and_enable_dhcp())