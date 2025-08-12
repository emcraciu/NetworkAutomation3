import telnetlib3
HOST = '92.81.55.146'
PORT = 5041

async def connect_to_device(host, port):
    reader, writer = await telnetlib3.open_connection(host, port)

