import asyncio
import time
from ipaddress import ip_address

import telnetlib3

from lib.connectors.telnet_con import TelnetConnection

HOST= '92.81.55.146'
PORT='5090'
command = 'show running-config'
hostname = "IOU1#"

router_ports=[]

def clean_lines(lines: str):
    return '\n'.join(
        line for line in lines.splitlines()
        if '--More--' not in line
        and '\x08' not in line
        and command not in line
        and hostname not in line
    ) + '\n'

conn=TelnetConnection(HOST,PORT)

async def connect_to_device(host, port):
    await conn.connect_to_device()
    conn.writer.write('\n')
    response = await conn.readuntil("IOU1#")
    if "IOU1#" in response:
        conn.writer.write('sh ip int br\n')
        response = await conn.readuntil("IOU1#")
        lines=response.splitlines()
        for line in lines:
            if 'unassigned' in line:
                columns=line.split(' ')
                router_ports.append(columns[0])
        print(router_ports)

async def assign_ip_address(host, port):
    ip_addr='192.168.10.'
    mask='255.255.255.0'
    last_byte=12
    await conn.connect_to_device()
    conn.writer.write('\n')
    response = await conn.readuntil("IOU1#")
    if "IOU1#" in response:
        if len(router_ports)>0:
            conn.writer.write('conf t\n')
            response = await conn.readuntil("IOU1(config)#")
            if "IOU1(config)#" in response:
                for r_ports in router_ports:
                    conn.writer.write(f"int {r_ports}\n")
                    response = await conn.readuntil("IOU1(config-if)#")
                    if "IOU1(config-if)#" in response:
                        ip_addr+=str(last_byte)
                        conn.writer.write(f"ip address {ip_addr} {mask}\n")
                        last_byte+=1
                    conn.writer.write("exit\n")
                    ip_addr='192.168.10.'

async def configure_dhcp(host, port):
    await conn.connect_to_device()
    conn.writer.write('\n')
    response = await conn.readuntil("IOU1(config)#")
    if "IOU1(config)#" in response:
        conn.writer.write('ip dhcp pool test1\n')
        conn.writer.write('network 192.168.10.30 255.255.255.0\n')
        conn.writer.write('default-router 192.168.1.1\n')
        conn.writer.write('dns-server 8.8.8.8\n')
        conn.writer.write('domain-name savnet.ro\n')
        conn.writer.write('exit\n')
        conn.writer.write('int e0/1\n')
        response = await conn.readuntil("IOU1(config-if)#")
        if "IOU1(config-if)#" in response:
            conn.writer.write('ip address dhcp\n')
            conn.writer.write('exit\n')

async def configure_ssh(host, port):
    await conn.connect_to_device()
    conn.writer.write('\n')
    response = await conn.readuntil("IOU1(config)#")
    if "IOU1(config)#" in response:
        conn.writer.write('username user password pass\n')
        conn.writer.write('hostname IOU1\n')
        conn.writer.write('ip domain name savnet.ro\n')
        conn.writer.write('enable secret pass\n')
        conn.writer.write('crypto key generate rsa modulus 2048\n')
        response = await conn.readuntil("IOU1(config)#")
        if "IOU1(config)#" in response:
            conn.writer.write('line vty 0 4\n')
            conn.writer.write('transport input ssh\n')
            conn.writer.write('login local\n')
            conn.writer.write('exit\n')
            conn.writer.write('exit\n')



asyncio.run(connect_to_device(HOST, PORT))
asyncio.run(assign_ip_address(HOST, PORT))
asyncio.run(configure_dhcp(HOST, PORT))
asyncio.run(configure_ssh(HOST, PORT))