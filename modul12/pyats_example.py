import asyncio
import subprocess
import time
from multiprocessing import Queue

from pyats import aetest, topology

from lib.connectors.rest_con import RESTConnector
from lib.connectors.telnet_con import TelnetConnection

q = Queue()
# import yaml
#
# with open('testbed.yaml', 'r') as yaml_file:
#     data = yaml.safe_load(yaml_file)
#     print(data)
import sys
print(sys.path)


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

    # @aetest.subsection
    # def bring_up_server_interface(self, steps):
    #     # tb = self.parent.parameters.get('tb')
    #     server = self.tb.devices['UbuntuServer']
    #     for intf_name, intf in server.interfaces.items():
    #         # intf = server.interfaces[interface]
    #         with steps.start(f'Bring up interface {intf_name}'):
    #             subprocess.run(['sudo', 'ip', 'addr', 'add', f'{intf.ipv4}', 'dev', f'{intf_name}'])
    #             subprocess.run(['sudo', 'ip', 'link', 'set', 'dev', f'{intf_name}', 'up'])
    #
    #     with steps.start('Add routes'):
    #         for device in self.tb.devices:
    #             if self.tb.devices[device].type != 'router':
    #                 continue
    #             gateway = self.tb.devices[device].interfaces['initial'].ipv4.ip.compressed
    #             for interface in self.tb.devices[device].interfaces:
    #                 if self.tb.devices[device].interfaces[interface].link.name == 'management':
    #                     continue
    #                 subnet = self.tb.devices[device].interfaces[interface].ipv4.network.compressed
    #                 subprocess.run(['sudo', 'ip', 'route', 'add', f'{subnet}', 'via', f'{gateway}'])

    # @aetest.subsection
    # def bring_up_server_interface(self, steps):
    #     for device in self.tb.devices:
    #         if self.tb.devices[device].type != 'router':
    #             continue
    #         with steps.start(f'Bring up interface {device}', continue_=True):
    #
    #             for interface in self.tb.devices[device].interfaces:
    #                 if self.tb.devices[device].interfaces[interface].link.name != 'management':
    #                     continue
    #
    #                 conn_class = self.tb.devices[device].connections.get('telnet', {}).get('class', None)
    #                 assert conn_class, f'No connection for device {device}'
    #
    #                 ip = self.tb.devices[device].connections.telnet.ip
    #                 port = self.tb.devices[device].connections.telnet.port
    #
    #                 conn: TelnetConnection = conn_class(ip, port)
    #                 async def conf():
    #                     await conn.connect()
    #                     time.sleep(1)
    #                     await conn.configure(q)
    #                 asyncio.run(conf())

    @aetest.subsection
    def connect_via_rest(self, steps):
        with steps.start("Connect via rest"):
            for device in self.tb.devices:
                if self.tb.devices[device].type != 'router':
                    continue
                if "rest" not in self.tb.devices[device].connections:
                    continue
                for interface in self.tb.devices[device].interfaces:
                    if self.tb.devices[device].interfaces[interface].link.name != 'management':
                        continue
                    conn_class: RESTConnector = self.tb.devices[device].connections["rest"]['class']
                    conn_data = self.tb.devices[device].connections["rest"]
                    conn_obj = conn_class(
                        ip=conn_data.ip.compressed,
                        port=conn_data.port,
                        username=conn_data.credentials.login['username'],
                        password=conn_data.credentials.login['password'],
                    )
                    conn_obj.connect()



class ConfigureInterfaces(aetest.Testcase):

    @aetest.setup
    def configure(self):
        tb = self.parent.parameters['tb']
        conn = tb.devices.IOU1.connections.telnet['class']
        print(conn)


if __name__ == '__main__':
    aetest.main()
