from sergiu_oprea_proiect.lib.connectors.telnet_con import TelnetConnection
import asyncio
from pyats import aetest, topology
from sergiu_oprea_proiect.path_helper import resource
import logging
from ssh_comms import commands

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

async def refuse_auto_conf(conn):
        conn.writer.write('\n')
        await asyncio.sleep(0.3)
        conn.writer.write('no\n')
        await asyncio.sleep(7)
        conn.writer.write('\n')
        await asyncio.sleep(15)
        conn.writer.write('\n')
        await asyncio.sleep(3)
        log.info('done with refusing auto-conf')

async def erase_startup_conf_and_reload(conn):
    conn.writer.write('erase startup-config\n')
    await asyncio.sleep(0.2)
    conn.writer.write('\n')
    await asyncio.sleep(0.2)
    conn.writer.write('reload\n')
    await asyncio.sleep(0.2)
    response = await conn.reader.read(1000)
    if 'System configuration has been modified. Save? [yes/no]' in response:
        conn.writer.write('no\n')
    conn.writer.write('\n')
    log.info('waiting for reloading...')
    await conn.read_until('initial configuration dialog')

async def preconfig(conn):
    await conn.connect()
    conn.writer.write('\r')
    await asyncio.sleep(1)
    response = await conn.reader.read(1000)
    log.info(response)
    if 'initial configuration dialog' in response:
        await refuse_auto_conf(conn)
    else:
        conn.writer.write('enable\n')
        await asyncio.sleep(0.2)
        conn.writer.write('\t')
        if '(config' in response:
            conn.write('end\n')
            await asyncio.sleep(0.2)
        conn.writer.write('show startup-config\n')
        await asyncio.sleep(0.2)
        response = await conn.reader.read(1000)
        if not 'startup-config is not present' in response:
            conn.writer.write('\t')
            await erase_startup_conf_and_reload(conn)
            await refuse_auto_conf(conn)

    conn.close()

async def configure(conn: TelnetConnection, tb, device):
    await conn.connect()
    conn.write('\r')
    conn.write('\t')
    result = await conn.read(1000)
    conn.writer.write('enable\n')

    await asyncio.sleep(0.5)
    if '(config' in result:
        conn.write('end\n')
        await asyncio.sleep(0.2)

    conn.write('\n')
    await asyncio.sleep(2)
    result = await conn.read(10000)
    if 'Router#' in result or 'Router>' in result:
        for interface in tb.devices[device].interfaces:
            if tb.devices[device].interfaces[interface].link.name != 'management':
                continue
            mgmt_ip = tb.devices[device].interfaces[interface].ipv4.ip.compressed
            mgmt_mask = tb.devices[device].interfaces[interface].ipv4.netmask.exploded
            conn.write('conf t\n')
            await conn.read_until(f'Router(config)#')
            conn.write(f'int {interface}\n')
            await conn.read_until(f'Router(config-if)#')
            conn.write(f'ip add {mgmt_ip} {mgmt_mask}\n')
            await conn.read_until(f'Router(config-if)#')
            conn.write('no shutdown\n')
            await conn.read_until(f'Router(config-if)#')
            conn.write('exit\n')
            await conn.read_until(f'Router(config)#')
            conn.write(f'hostname {device}\n')
            await conn.read_until(f'{device}(config)#')
            conn.write('line con 0\n')
            await conn.read_until(f'{device}(config-line)#')
            conn.write('logg syn\n')
            await conn.read_until(f'{device}(config-line)#')
            conn.write('end\n')
            await conn.read_until(f'{device}#')
            conn.close()
    else: conn.close()

async def preconfigurer(server_ip, router_ports):
    await asyncio.gather(*(preconfig(TelnetConnection(server_ip, x)) for x in router_ports.values()))

async def configurer(tb, router_ports):
    await asyncio.gather(
        *(
            configure(TelnetConnection(tb.custom.server_ip, port), tb, device) for device, port in router_ports.items()
        )
    )

class RouterConfig(aetest.Testcase):
    @aetest.setup
    def load_testbed(self, steps):
        with steps.start("Load testbed"):
            testbed_path = str(resource("testbeds/telnet_testbed.yaml"))
            self.tb = topology.loader.load(testbed_path)
            log.info("Successfully loaded testbed")
            self.parent.parameters.update(tb=self.tb)

    @aetest.test
    def get_testbed_routers(self, steps):
        with steps.start("Get router ports"):
            self.routers = {}
            for i in self.tb.devices:
                if self.tb.devices[i].type != 'router':
                    continue
                self.routers.update({i:self.tb.devices[i].connections.telnet.port})
            log.info(f"Routers: {self.routers}")

    @aetest.test
    def router_preconfig(self, steps):
        with steps.start("Initial configuration"):
            asyncio.run(preconfigurer(self.tb.custom.server_ip, self.routers))

    @aetest.test
    def router_config(self, steps):
        with steps.start("Router configuration"):

            asyncio.run(configurer(self.tb, self.routers))

    @aetest.test
    def ssh_config(self, steps):
        self.ssh_configs = {}
        with steps.start('Trying to bring up management ints of devices', continue_=True):
            for device in self.tb.devices:
                if self.tb.devices[device].type != 'router':
                    continue
                for interface in self.tb.devices[device].interfaces:
                    if self.tb.devices[device].interfaces[interface].link.name == 'management':
                        intf_obj = self.tb.devices[device].interfaces[interface]
                        con = self.tb.devices[device].connections.get('telnet', {}).get('class', {})
                        assert con, 'no telnet connection present for device'

                        ip = self.tb.devices[device].connections.telnet.get('ip')
                        port = self.tb.devices[device].connections.telnet.get('port')

                        assert ip and port, 'ip or port nonexistent'

                        formated_comms = list(
                            map(
                                lambda s: s.format(
                                    ip=intf_obj.ipv4.ip.compressed,
                                    sm=intf_obj.ipv4.netmask.exploded,
                                    interface=interface,
                                    hostname=device,
                                    domain=self.tb.devices[device].custom.get('domain', ''),
                                    username=self.tb.devices[device].connections.telnet.credentials.login.username,
                                    password=self.tb.devices[
                                        device].connections.telnet.credentials.login.password.plaintext
                                ),
                                commands
                            )
                        )

                        self.ssh_configs.update({device:(con(ip.compressed, port),formated_comms)})

            async def setup(conn, formated_comms):
                await conn.connect()
                await conn.execute_commands(formated_comms, '#')
            async def worker(ssh_configs):
                await asyncio.gather(*(setup(conn, comms) for conn, comms in ssh_configs.values()))
            asyncio.run(worker(self.ssh_configs))

if __name__ == '__main__':
    aetest.main()