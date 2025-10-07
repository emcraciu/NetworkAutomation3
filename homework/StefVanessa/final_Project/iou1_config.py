from pyats import aetest, topology
from genie.libs.conf.interface.iosxe import Interface
from pyats.topology import Device

def configure_dhcp_pool(device: Device, pool_name="UBUNTU_DOCKER1_POOL", network="192.168.210.0 255.255.255.0", default_router="192.168.210.10", dns_server="8.8.8.8"):
    """
    Configure a DHCP pool on the IOS router for Ubuntu Docker clients.
    """
    dhcp_config = [
        f"ip dhcp excluded-address {default_router}",
        f"ip dhcp pool {pool_name}",
        f"network {network}",
        f"default-router {default_router}",
        f"dns-server {dns_server}",
    ]

    print("⚙️  Configuring DHCP pool...")
    device.configure(dhcp_config)
    print(f"✅ DHCP pool '{pool_name}' configured successfully.")

class CommonSetup(aetest.CommonSetup):
    @aetest.subsection
    def load_testbed(self, steps):
        with steps.start("Load testbed"):
            tb = topology.loader.load('testbed.yaml')
            self.parent.parameters.update(tb=tb)


class ConfigureIOU1(aetest.Testcase):
    @aetest.setup
    def connect(self, steps):
        tb = self.parent.parameters.get("tb")
        self.dev: Device = tb.devices.IOU1
        self.dev.connect(via="cli", log_stdout=True)

    @aetest.test
    def configure_interfaces(self, steps):
        for intf_name, intf_data in self.dev.interfaces.items():
            with steps.start(f"Configure {intf_name}"):
                intf = Interface(name=intf_name)
                intf.device = self.dev
                intf.ipv4 = intf_data.ipv4
                intf.shutdown = False
                config = intf.build_config(apply=False)
                self.dev.configure(config.cli_config.data)
                print(config)
                print(f" Configured {intf_name} with {intf_data.ipv4} and no shutdown")

    @aetest.test
    def enable_ssh(self, steps):
        with steps.start("Enable SSH"):
            ssh_cfg = [
                "hostname IOU1",
                "ip domain name cisco.com",
                "crypto key generate rsa modulus 2048",
                "ip ssh version 2",
                "username cisco privilege 15 secret cisco",
                "line vty 0 4",
                "transport input ssh",
                "login local"
            ]
            self.dev.configure(ssh_cfg)

    @aetest.test
    def configure_dhcp(self, steps):
        with steps.start("Configure DHCP Pools"):
            configure_dhcp_pool(self.dev)

    @aetest.test
    def verify_interfaces(self, steps):
        output = self.dev.execute("show ip interface brief")
        print(output)

if __name__ == '__main__':
    aetest.main()
