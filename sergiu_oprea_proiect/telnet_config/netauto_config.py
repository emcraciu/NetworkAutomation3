from pyats import aetest, topology
from sergiu_oprea_proiect.path_helper import resource
import logging
import subprocess

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

class NetAutoConfig(aetest.Testcase):
    @aetest.setup
    def load_testbed(self, steps):
        with steps.start("Load testbed"):
            testbed_path = str(resource("testbeds/telnet_testbed.yaml"))
            self.tb = topology.loader.load(testbed_path)
            log.info("Successfully loaded testbed")
            self.parent.parameters.update(tb=self.tb)

    @aetest.test
    def netauto_address_and_routes(self, steps):
        server = self.tb.devices['NetAuto']

        for interface in server.interfaces:
            intf = server.interfaces[interface]
            with steps.start("Bring up interface {interface.name}"):
                subprocess.run(['sudo', 'ip', 'addr', 'add', f'{intf.ipv4}', 'dev', f'{interface}'])
                subprocess.run(['sudo', 'ip', 'link', 'set', 'dev', f'{interface}', 'up'])

            with steps.start('Add routes'):
                for device in self.tb.devices:
                    if self.tb.devices[device].type not in ['router', 'ftd']:
                        continue
                    gateway = self.tb.devices[device].interfaces['initial'].ipv4.ip.compressed
                    for interface in self.tb.devices[device].interfaces:
                        if self.tb.devices[device].interfaces[interface].link.name == 'management':
                            continue
                        subnet = self.tb.devices[device].interfaces[interface].ipv4.network.compressed
                        subprocess.run(['sudo', 'ip', 'route', 'add', f'{subnet}', 'via', f'{gateway}'])

if __name__ == '__main__':
    aetest.main()