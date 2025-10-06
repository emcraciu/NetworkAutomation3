import asyncio
import logging

from netutils.ip import netmask_to_wildcardmask
from pyats import aetest, topology

from sergiu_oprea_proiect.lib.connectors.ssh_con import SshConnection
from sergiu_oprea_proiect.path_helper import resource

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

async def ospf(conn, tb, device):
    conn.connect()
    await asyncio.sleep(1)
    conn.create_shell()
    await asyncio.sleep(1)
    conn.send(f'conf t\n')
    await asyncio.sleep(1)
    for intf in tb.devices[device].interfaces:
        interface = tb.devices[device].interfaces[intf]
        ip = interface.ipv4.ip.compressed
        mask = interface.ipv4.netmask.exploded
        conn.send(f'int {intf}\n')
        await asyncio.sleep(0.3)
        conn.send(f'ip add {ip} {mask}\n')
        await asyncio.sleep(0.3)
        conn.send('no shut\n')
        await asyncio.sleep(0.3)
    conn.send('exit\n')
    await asyncio.sleep(1)
    conn.send(f'router ospf 1\n')
    await asyncio.sleep(1)
    conn.send(f'router-id {tb.devices[device].interfaces['Loopback0'].ipv4.ip.compressed}\n')
    await asyncio.sleep(1)
    for intf in tb.devices[device].interfaces:
        curr_intf = tb.devices[device].interfaces[intf]
        network = curr_intf.ipv4.network.network_address.compressed
        wildcardmask = netmask_to_wildcardmask(curr_intf.ipv4.netmask.exploded)
        log.info(f'Wildcard mask: {wildcardmask} and network: {network}')
        conn.send(f'network {network} {wildcardmask} area 0\n')
        await asyncio.sleep(1)
    conn.close()

async def worker(tb, routers):
    await asyncio.gather(*
        (
            ospf(
                SshConnection(
                    ip,
                    22,
                    tb.devices[device].connections.telnet.credentials.login.username,
                    tb.devices[device].connections.telnet.credentials.login.password.plaintext
                ),
                tb,
                device
            )
            for device, ip in routers.items()
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
        with steps.start("Get router ips"):
            self.routers = {}
            for i in self.tb.devices:
                if self.tb.devices[i].type != 'router':
                    continue
                self.routers.update({i:self.tb.devices[i].connections.ssh.ip.compressed})
            log.info(f"Routers: {self.routers}")

    @aetest.test
    def router_config(self):
        asyncio.run(worker(self.tb, self.routers))


if __name__ == "__main__":
    aetest.main()