import asyncio
import subprocess
import time
from multiprocessing import Queue

from pyats import aetest, topology

from lib.connectors.rest_con import RESTConnector

q = Queue()

import sys

print(sys.path)


class CommonSetup(aetest.CommonSetup):
    @aetest.subsection
    def load_testbed(self, steps):
        with steps.start("Load testbed"):
            self.tb = topology.loader.load('testbed.yaml')
            self.parent.parameters.update(tb=self.tb)

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
                    conn_data = self.tb.devices[device].connections["rest"]

                    conn: RESTConnector = self.tb.devices[device].connections["rest"]['class'](
                        ip=conn_data.ip.compressed,
                        port=conn_data.port,
                        username=conn_data.credentials.login['username'],
                        password=conn_data.credentials.login['password'].plaintext,
                    )
                    conn.connect()
                    print(conn.get_interface('Gi1'))


class ConfigureInterfaces(aetest.Testcase):

    @aetest.setup
    def configure(self):
        tb = self.parent.parameters['tb']
        conn = tb.devices.IOU1.connections.telnet['class']
        print(conn)


if __name__ == '__main__':
    aetest.main()
