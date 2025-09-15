from pyats import aetest, topology

from lib.connectors.ssh_con import SshConnection


class CommonSetup(aetest.CommonSetup):
    @aetest.subsection
    def load_testbed(self, steps):
        with steps.start("Load testbed"):
            tb = topology.loader.load('testbed.yaml')
            self.parent.parameters.update(tb=tb)


class ConfigureGenie(aetest.Testcase):
    @aetest.setup
    def connect(self, steps):
        tb = self.parent.parameters.get("tb")
        conn: SshConnection = tb.devices.CSR.connections.ssh['class'](
            host=str(tb.devices.CSR.connections.ssh['ip']),
            port=str(tb.devices.CSR.connections.ssh['port']),
            username=tb.devices.CSR.connections.ssh.credentials.default['username'],
            password=tb.devices.CSR.connections.ssh.credentials.default['password'].plaintext,
        )
        conn.connect()
        conn.configure()


if __name__ == '__main__':
    aetest.main()
