import asyncio

import telnetlib3
HOST = '92.81.55.146'
PORT = 5041

async def connect_to_device(host, port):
    reader, writer = await telnetlib3.open_connection(host, port)
    writer.write('\n')
    response = await reader.readuntil(b"IOU1#")
    # response = await asyncio.wait_for(reader.read(200), timeout=2)
    print(response)
    if 'IOU1#' in response.decode():
        writer.write("show interfaces Ethernet1/1\n ")
        response = await  reader.readuntil(b"IOU1#")

        # print(type(response))
        # print(response)
    # writer.close()
    # await writer.wait_closed()

asyncio.run(connect_to_device(HOST, PORT))

