import subprocess

from pyats import aetest, topology
# import yaml
#
# with open('testbed.yaml', 'r') as yaml_file:
#     data = yaml.safe_load(yaml_file)
#     print(data)
# import sys
# print(sys.path)


class CommonSetup(aetest.CommonSetup):
    @aetest.subsection
    def load_testbed(self, steps):
        with steps.start("Load testbed"):
            self.tb = topology.loader.load('testbed.yaml')
            # dev = self.tb.devices.IOU1
            # dev = self.tb.devices['IOU1']
            # print(self.tb)
            self.parent.parameters.update(tb=self.tb)
            # x = {}
            # x.update(tb=self.tb)

    @aetest.subsection
    def bring_up_server_interface(self, steps):
        # tb = self.parent.parameters.get('tb')
        server = self.tb.devices['UbuntuServer']
        for interface in server.interfaces:
            intf = server.interfaces[interface]
            with steps.start("Bring up interface {interface.name}"):
                subprocess.run(['sudo', 'ip', 'addr', 'add', f'{intf.ipv4}', 'dev', f'{interface}'])
                subprocess.run(['sudo', 'ip', 'link', 'set', 'dev', f'{interface}', 'up'])

            with steps.start("Add routes"):
                subprocess.run(['sudo', 'ip', 'route', 'add', '192.168.201.0/24', 'via', '192.168.200.1'], )

class ConfigureInterfaces(aetest.Testcase):

    @aetest.setup
    def configure(self):
        tb = self.parent.parameters['tb']
        conn = tb.devices.IOU1.connections.telnet['class']
        print(conn)


if __name__ == '__main__':
    aetest.main()

