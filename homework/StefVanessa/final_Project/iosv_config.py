from pyats import aetest, topology
from genie.libs.conf.interface.ios import Interface  # pentru IOSv


class CommonSetup(aetest.CommonSetup):
    @aetest.subsection
    def load_testbed(self, steps):
        tb = topology.loader.load('testbed.yaml')
        self.parent.parameters.update(tb=tb)


class ConfigureIOSv(aetest.Testcase):
    @aetest.setup
    def connect(self, steps):
        tb = self.parent.parameters.get("tb")
        self.dev = tb.devices.IOSv
        self.dev.connect(via="cli", log_stdout=True)

    @aetest.test
    def configure_interfaces(self, steps):
        for intf_name, intf_data in self.dev.interfaces.items():
            with steps.start(f"Configure {intf_name}"):
                intf = Interface(name=intf_name)
                intf.device = self.dev
                intf.ipv4 = intf_data.ipv4
                intf.shutdown = False

                cfg = intf.build_config(apply=False)
                try:
                    self.dev.configure(cfg)
                except Exception:
                    self.dev.configure(cfg.cli_config.data)
                print(f" Configured {intf_name} with {intf_data.ipv4} and no shutdown")

    @aetest.test
    def enable_ssh(self, steps):
        with steps.start("Enable SSH"):
            ssh_cfg = [
                "hostname IOSv",
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
    def verify_interfaces(self, steps):
        out = self.dev.execute("show ip interface brief")
        print(out)


if __name__ == '__main__':
    aetest.main()
