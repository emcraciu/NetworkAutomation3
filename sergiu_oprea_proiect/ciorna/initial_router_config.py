from sergiu_oprea_proiect.lib.connectors.telnet_con import TelnetConnection
import asyncio

server_ip = '92.81.55.146'
router_ports = {'IOU': 5065, 'IOS': 5090, 'CSR': 5067}
async def connect_to_router(conn):
    await conn.connect()
    conn.writer.write('\n')
    await asyncio.sleep(1)
    response = await conn.reader.read(100)
    print(response)
    if 'initial configuration dialog' in response:
        print('here')
        conn.writer.write('no\n')
        await asyncio.sleep(5)
        conn.writer.write('\n')
        print('gata')
    conn.close()
# iou_conn = TelnetConnection(server_ip, router_ports['CSR'])
async def worker():
    await asyncio.gather(*(connect_to_router(TelnetConnection(server_ip, x)) for x in router_ports.values()))


asyncio.run(worker())

