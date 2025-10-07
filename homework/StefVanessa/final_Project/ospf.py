from pyats import aetest, topology
from genie.libs.ops.interface.interface import Interface
from lib.connectors.swagger_connection import SwaggerConnection
import requests
#FTD prin swagger

class CommonSetup(aetest.CommonSetup):
    """Faza comună - încărcare testbed"""
    @aetest.subsection
    def load_testbed(self, steps):
        with steps.start("Load testbed"):
            tb = topology.loader.load("ospf_testbed.yaml")
            self.parent.parameters.update(tb=tb)


class ConfigureOSPF(aetest.Testcase):

    @aetest.setup
    def connect(self, steps):
        tb = self.parent.parameters.get("tb")
        self.devices = tb.devices

        for name, dev in self.devices.items():
            if dev.os == "generic":

                print(f"Initiez conexiune Swagger pentru {name}")
                dev.swagger = SwaggerConnection(dev).connect()
                continue

            with steps.start(f"Conectare la {name}"):
                try:
                    dev.connect(via="cli", log_stdout=True)
                except Exception as e:
                    self.failed(f"Nu pot conecta {name}: {e}")

    @aetest.test
    def check_interfaces(self, steps):
        self.ready_devices = []

        for name, dev in self.devices.items():
            if dev.os == "generic":
                print(f" Sar peste verificarea interfețelor pe {name} (Swagger, fără Genie OPS)")
                self.ready_devices.append(dev)
                continue

            if dev.os in ["ios", "iosxe"]:
                with steps.start(f"Verific interfețele pe {name} (IOS/IOSXE)"):
                    try:
                        parsed = dev.parse("show ip interface brief")
                        print(f" Parsed interfețe {name}: {parsed}")
                    except Exception as e:
                        print(f" Nu pot parsa interfețele pe {name}: {e}")
                        continue

                    ok_found = False
                    for intf, data in parsed.get("interface", {}).items():
                        ip = data.get("ip_address")
                        status = data.get("status")
                        protocol = data.get("protocol")

                        if ip and ip != "unassigned" and status == "up" and protocol == "up":
                            ok_found = True
                            print(f" {name} - {intf} este valid (IP {ip}, UP/UP)")

                    if ok_found:
                        self.ready_devices.append(dev)
                    else:
                        print(f" {name} nu are nicio interfață validă pentru OSPF")

            elif dev.os == "linux":
                with steps.start(f"Verific interfețele pe {name} (Linux)"):
                    try:
                        output = dev.execute("ip -br addr")
                        print(f" Output brut {name}:\n{output}")
                    except Exception as e:
                        print(f" Nu pot rula comanda pe {name}: {e}")
                        continue

                    ok_found = False
                    for line in output.splitlines():
                        parts = line.split()
                        if len(parts) < 3:
                            continue
                        intf, state, *rest = parts
                        if intf == "lo":  # ignor loopback
                            continue
                        ip = None
                        for p in rest:
                            if "/" in p:
                                ip = p
                                break
                        if ip and state.upper() == "UP":
                            ok_found = True
                            print(f" {name} - {intf} este valid (IP {ip}, {state})")

                    if ok_found:
                        self.ready_devices.append(dev)
                    else:
                        print(f"⏭ {name} nu are nicio interfață validă pentru OSPF")



    @aetest.test
    def configure_ospf(self, steps):
        """Configurează OSPF pe device-urile pregătite"""
        for dev in self.ready_devices:
            with steps.start(f"Configurez OSPF pe {dev.name}"):

                ospf_data = dev.custom.get("ospf", {})
                router_id = ospf_data.get("router_id", "1.1.1.1")
                networks = ospf_data.get("networks", ["0.0.0.0 255.255.255.255 area 0"])

                if dev.os in ["ios", "iosxe"]:
                    # Config clasic Cisco IOS/IOS-XE
                    ospf_cfg = [f"router ospf 1", f"router-id {router_id}"]
                    for net in networks:
                        ospf_cfg.append(f"network {net}")

                    dev.configure(ospf_cfg)
                    dev.execute("write memory")
                    print(f" OSPF configurat pe {dev.name} (IOS/IOS-XE)")

                elif dev.os == "linux":
                    # Config pe Linux (FRR/Quagga)
                    dev.execute(f"sudo vtysh -c 'configure terminal' -c 'router ospf' -c 'router-id {router_id}'")
                    for net in networks:
                        dev.execute(f"sudo vtysh -c 'configure terminal' -c 'router ospf' -c 'network {net}'")
                    dev.execute("sudo vtysh -c 'write'")
                    print(f" OSPF configurat pe {dev.name} (Linux/FRR)")

                elif dev.os == "generic":
                    # Config pe FTD via Swagger
                    url = f"{dev.swagger._url}/api/fdm/v6/devicesettings/default/routing/ospf"

                    payload = {
                        "routerId": router_id,
                        "networks": [{"network": net} for net in networks]
                    }
                    try:
                        resp = requests.post(
                            url,
                            headers=dev.swagger._headers,
                            json=payload,
                            verify=False
                        )
                        if resp.status_code in [200, 201]:
                            print(f" OSPF configurat pe {dev.name} (FTD). Răspuns: {resp.json()}")
                        else:
                            print(f" Eroare FTD {dev.name}: {resp.status_code} - {resp.text}")
                    except Exception as e:
                        print(f" Eroare la configurarea OSPF pe {dev.name}: {e}")

                else:
                    print(f" OS necunoscut pentru {dev.name}, sar peste configurare")


if __name__ == "__main__":
    aetest.main()