from pyats import aetest, topology
# from genie.libs.ops.interface.interface import Interface
import time

from sender_email import send_email


class CommonSetup(aetest.CommonSetup):
    """Common phase – load testbed"""
    @aetest.subsection
    def load_testbed(self, steps):
        with steps.start("Load testbed"):
            tb = topology.loader.load("testbed_ospf.yaml")
            self.parent.parameters.update(tb=tb)


class ConfigureOSPF(aetest.Testcase):

    @aetest.setup
    def connect(self, steps):
        tb = self.parent.parameters.get("tb")
        self.devices = tb.devices

        for name, dev in self.devices.items():
            # connect only to devices with CLI (IOS/IOS-XE, Linux/FRR)
            if dev.os in ["ios", "iosxe", "linux"]:
                with steps.start(f"Connect to {name}"):
                    dev.connect(via="cli", log_stdout=True)
            else:
                print(f"[INFO] Skipping {name} (os={dev.os}) — FTD/other excluded from script.")

    @aetest.test
    def configure_ospf(self, steps):
        """Configure OSPF on the devices in the testbed (excluding FTD)"""
        for name, dev in self.devices.items():
            with steps.start(f"Configure OSPF on {name}"):
                if dev.os not in ["ios", "iosxe", "linux"]:
                    print(f"[INFO] {name}: ignored (os={dev.os})")
                    continue

                ospf_data = dev.custom.get("ospf", {})
                router_id = ospf_data.get("router_id", "1.1.1.1")
                networks  = ospf_data.get("networks", [])

                if dev.os in ["ios", "iosxe"]:
                    cfg = [f"router ospf 1", f"router-id {router_id}"]
                    for net in networks:
                        cfg.append(f"network {net}")
                    dev.configure(cfg)
                    print(f" OSPF configured on {name} (IOS/IOS-XE)")
                    try:
                        send_email(" OSPF Config", f"OSPF configured on {name}")
                    except Exception:
                        pass

                elif dev.os == "linux":
                    dev.execute(f"sudo vtysh -c 'configure terminal' -c 'router ospf' -c 'router-id {router_id}'")
                    for net in networks:
                        dev.execute(f"sudo vtysh -c 'configure terminal' -c 'router ospf' -c 'network {net}'")
                    print(f" OSPF configured on {name} (Linux/FRR)")
                    try:
                        send_email(" OSPF Config", f"OSPF configured on {name}")
                    except Exception:
                        pass


if __name__ == "__main__":
    aetest.main()
