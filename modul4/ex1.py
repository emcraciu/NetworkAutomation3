# check IP address for all interfaces on IOU1
import asyncio

import telnetlib3

HOST = '92.81.55.146'
PORT = 5041  # replace with yours


# Elvis
async def connect_to_device1(host, port):
    reader, writer = await telnetlib3.open_connection(host, port)
    writer.write('\n')
    response = await reader.readuntil(b"IOU1#")
    print(response)
    for port in range(0, 2):
        for port_number in range(0, 4):
            writer.write(f"show int e{port}/{port_number}\n\t")
            response = await reader.readuntil(b"IOU1#")
            for line in response.splitlines():
                if b"Internet address is" in line:
                    ip = line.decode().split()[-1]
                    print(ip)


asyncio.run(connect_to_device1(HOST, PORT))


# Bogdan Rad
async def connect_to_device2(host, port):
    reader, writer = await telnetlib3.open_connection(host, port)
    writer.write('\n')
    response = await reader.readuntil(b"IOU1#")
    print(response)
    if "IOU1#" in response.decode():
        writer.write('sh ip int br\n')
        response = await reader.readuntil(b"IOU1#")
        decoded = response.decode()
        for line in decoded.splitlines():
            if "Ethernet" in line or "Serial" in line:
                parts = line.split()
                if parts[1] != "unassigned":
                    print(f"{parts[0]} has an IP address of : {parts[1]}")


asyncio.run(connect_to_device2(HOST, PORT))

# Paul
router_ports = ['Ethernet0/0', 'Ethernet0/1', 'Ethernet0/2', 'Ethernet0/3',
                'Ethernet1/0', 'Ethernet1/1', 'Ethernet1/2', 'Ethernet1/3']


async def connect_to_device(host, port):
    reader, writer = await telnetlib3.open_connection(host, port)
    writer.write('\n')
    response = await reader.readuntil(b"IOU1#")
    if 'IOU1#' in response.decode():
        for r_port in router_ports:
            writer.write("show int " + r_port + "\n\t")
            response = await reader.readuntil(b"IOU1#")
            if "Internet address is" in response.decode():
                tmp = response.decode().split('\n')
                response = tmp[3].split(' ')
                print(r_port, response[-1])
            else:
                print(f"{r_port} has no ip address")


asyncio.run(connect_to_device(HOST, PORT))

# Sergiu +1