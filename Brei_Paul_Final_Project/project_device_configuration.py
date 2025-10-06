"""Python script for automatically configuring
Ubuntu PCs and Cisco Networking devices (Routers, FTD)"""
import asyncio
import subprocess
import sys
import time
from ipaddress import IPv4Address
import bravado.exception

from pyats import aetest, topology
from pyats.aetest.steps import Step
from connectors.telnet_conn import TelnetConnection
from connectors.swagger_conn import SwaggerConnector
from Brei_Paul_Final_Project.tools import (router_config, static_route_config,
                                           dhcp_config, bad_csr_commands)

def show_cli_menu():
    """Display Menu Interface"""
    print("\n=== Device Configuration Menu ===")
    print("1. Configure Ubuntu Server (PC)")
    print("2. Configure Routers (IOU/IOSv/CSR)")
    print("3. Configure FTD Initial Setup")
    print("4. Configure FTD Interfaces")
    print("5. DEBUG: Bad CSR Configuration")
    print("6. Ping End Devices")
    print("7. Diagnose CSR")
    print("0. Exit")
    print("=================================\n")

    option = input("Enter your option: ")
    return option

def get_user_options():
    """Helper function for getting user options"""
    selected = set()
    while True:
        option = show_cli_menu()
        match option:
            case "1":
                selected.add("server")
            case "2":
                selected.add("routers")
            case "3":
                selected.add("ftd_initial")
            case "4":
                selected.add("ftd_interfaces")
            case "5":
                selected.add("bad_csr_config")
            case "6":
                selected.add("ping_end_devices")
            case "7":
                selected.add("diagnose")
            case "0":
                print("Exiting...")
                sys.exit(0)
            case _:
                print("Invalid option, try again.")
                continue

        another = input("Add another selection? (y/n): ").lower()
        if another != "y":
            break
    return selected

def create_ipv4(swagger, interface):
    """Ensure interface has ipv4.ipAddress initialized with HAIPv4Address if missing"""
    if not interface.ipv4:
        ipv4_model = swagger.get_model('InterfaceIPv4')
        interface.ipv4 = ipv4_model()

    if not interface.ipv4.ipAddress:
        ha_model = swagger.get_model('HAIPv4Address')
        interface.ipv4.ipAddress = ha_model(
            ipAddress=None,
            netmask=None,
            standbyIpAddress=None,
            type='haipv4address'
        )

    return interface

class CommonSetup(aetest.CommonSetup):
    """Main Pyats Class"""
    def find_gateway(self, device, intf_obj):
        """
        Find the correct gateway for a given device interface
        by matching link name parts against other devices' aliases.
        """
        link_name = intf_obj.link.name
        link_parts = link_name.split('_')

        for neighbor in self.tb.devices.values():
            if neighbor is device:
                continue
            if getattr(neighbor, "alias", None) in link_parts:
                for nbr_intf in neighbor.interfaces.values():
                    if nbr_intf.link.name == link_name:
                        return nbr_intf.ipv4.ip.compressed
        return None

    @aetest.subsection
    def load_testbed(self, steps):
        """Pyats function for loading the testbed"""
        with steps.start("Load testbed"):
            self.tb = topology.loader.load('testbeds/testbed.yaml')
            self.parent.parameters.update(tb=self.tb)

    @aetest.subsection
    def activate_server_interface(self, steps):
        """Activates the interface on the Ubuntu Server device"""
        server = self.tb.devices['UbuntuServer']
        for interface in server.interfaces:
            intf = server.interfaces[interface]
            with steps.start(f"Bring up interface {interface}", continue_=True) as step: #type: Step
                if "server" not in USER_SELECTION:
                    step.skipped("User skipped Ubuntu Server configuration")
                    return
                subprocess.run(['sudo', 'ip', 'addr',
                                'add', f'{intf.ipv4}', 'dev', f'{interface}'])
                subprocess.run(['sudo', 'ip', 'link',
                                'set', 'dev', f'{interface}', 'up'])

        with steps.start("Add routes", continue_=True) as step: #type: Step
            if "server" not in USER_SELECTION:
                step.skipped("User skipped Ubuntu Server configuration")
                return
            for device in self.tb.devices:
                if self.tb.devices[device].type not in ('router', 'ftd'):
                    continue
                try:
                    gateway = self.tb.devices[device].interfaces['initial'].ipv4.ip.compressed
                except KeyError:
                    gateway = self.tb.devices[device].interfaces['csr_initial'].ipv4.ip.compressed

                for interface in self.tb.devices[device].interfaces:
                    intf_obj = self.tb.devices[device].interfaces[interface]
                    if intf_obj.link.name=='management':
                        continue
                    subnet = intf_obj.ipv4.network.network_address.compressed

                    subprocess.run(
                        ['sudo', 'ip', 'route', 'add',
                         f'{subnet}', 'via', f'{gateway}',
                         'metric', '100'])

    @aetest.subsection
    def activate_routers(self, steps):
        """Applies basic router configuration"""
        is_csr = False
        csr_init = False
        for device in self.tb.devices:
            if self.tb.devices[device].type != 'router':
                continue
            with steps.start(f'Bring up interface {device}', continue_=True) as step: #type: Step
                if "routers" not in USER_SELECTION:
                    step.skipped("User skipped Ubuntu Server configuration")
                    return

                for interface in self.tb.devices[device].interfaces:
                    intf_obj=self.tb.devices[device].interfaces[interface]
                    conn_class=self.tb.devices[device].connections.get('telnet',{}).get('class')
                    assert conn_class,f'No connection for device {device}'
                    ip = self.tb.devices[device].connections.telnet.ip.compressed
                    port = self.tb.devices[device].connections.telnet.port

                    csr_commands=[]

                    if r'0/' not in intf_obj.name and intf_obj.link.name == "management":
                        csr_commands=['en','conf t', 'hostname CSR', 'exit']
                        is_csr=True

                    commands=router_config.interface_commands
                    intf_commands=list(map(
                        lambda s: s.format(
                            interface=interface,
                            ip=intf_obj.ipv4.ip.compressed,
                            sm=intf_obj.ipv4.netmask.exploded,
                        ),
                        commands
                    ))

                    ssh_commands=[]

                    if intf_obj.link.name == 'management':
                        commands=router_config.ssh_commands
                        ssh_commands=csr_commands+list(map(
                            lambda s: s.format(
                                hostname=self.tb.devices[device].custom.get('hostname', device),
                                domain=self.tb.devices[device].custom.get('domain',''),
                                username=self.tb.devices[device].connections
                                .telnet.credentials.login.username,
                                password=self.tb.devices[device].connections
                                .telnet.credentials.login.password.plaintext,
                                en_password=self.tb.devices[device].connections.telnet.
                                credentials.enable.password.plaintext,

                            ),
                            commands
                        ))

                    route_commands = []

                    if intf_obj.link.name !='management':
                        own_subnet = intf_obj.ipv4.network.network_address.compressed
                        own_subnet_third_byte=own_subnet.split('.')[2]
                        print(own_subnet)

                        if self.tb.devices[device].alias in intf_obj.link.name.split('_')[1]:
                            for i in range(210, int(own_subnet_third_byte), 10):
                                subnet="192.168." + str(i) + ".0"

                                mask = str(intf_obj.ipv4.netmask)

                                gateway = self.find_gateway(self.tb.devices[device], intf_obj)
                                print(gateway)
                                if not gateway:
                                    continue

                                route_commands += list(map(
                                    lambda s: s.format(subnet=subnet, mask=mask, gateway=gateway),
                                    static_route_config.commands
                                ))

                        if self.tb.devices[device].alias in intf_obj.link.name.split('_')[0]:
                            for i in range(int(own_subnet_third_byte)+10, 251, 10):
                                subnet="192.168." + str(i) + ".0"

                                mask = str(intf_obj.ipv4.netmask)

                                gateway = self.find_gateway(self.tb.devices[device], intf_obj)
                                print(gateway)
                                if not gateway:
                                    continue

                                route_commands += list(map(
                                    lambda s: s.format(subnet=subnet, mask=mask, gateway=gateway),
                                    static_route_config.commands
                                ))

                    dhcp_commands=[]

                    if self.tb.devices[device].alias=='iou':
                        if intf_obj.link.alias == 'guest1_iou':
                            commands=dhcp_config.dhcp_commands
                            dhcp_commands=list(map(
                                lambda s: s.format(
                                    name=self.tb.devices[device].custom.get('dhcp_pool_name',''),
                                    network=intf_obj.ipv4.network.network_address.compressed,
                                    gateway=intf_obj.ipv4.ip.compressed,
                                    dns_server=self.tb.devices[device].custom.get('dns_server',''),
                                    domain=self.tb.devices[device].custom.get('domain',''),
                                    excl_address=intf_obj.ipv4.ip.compressed
                                ),
                                commands
                            ))

                    formatted_commands = csr_commands + intf_commands
                    formatted_commands += ssh_commands + route_commands + dhcp_commands

                    conn: TelnetConnection = conn_class(ip, port)

                    async def setup():
                        """Applies basic router configuration"""
                        nonlocal csr_init
                        await conn.connect()
                        time.sleep(1)
                        if is_csr and not csr_init:
                            await conn.initialize_csr()
                            csr_init = True
                        await conn.enter_commands(formatted_commands, '#')
                    asyncio.run(setup())

    @aetest.subsection
    def configure_initial_ftd(self, steps):
        """Completes the initial configuration for the FTD device"""
        for device in self.tb.devices:
            if self.tb.devices[device].type != 'ftd':
                continue
            with steps.start(f'Bring up mgmt intf {device}', continue_=True) as step: # type: Step
                if "ftd_initial" not in USER_SELECTION:
                    step.skipped("User skipped Ubuntu Server configuration")
                    return
                for interface in self.tb.devices[device].interfaces:
                    if self.tb.devices[device].interfaces[interface].link.name != 'management':
                        continue

                    intf_obj = self.tb.devices[device].interfaces[interface]
                    conn_class = self.tb.devices[device].connections.get('telnet', {}).get('class')
                    assert conn_class, f'No connection for device {device}'
                    ip = self.tb.devices[device].connections.telnet.ip.compressed
                    port = self.tb.devices[device].connections.telnet.port
                    conn: TelnetConnection = conn_class(ip, port)
                    ftd_password=self.tb.devices[device].credentials.default.password.plaintext

                    async def setup():
                        await conn.connect()
                        time.sleep(1)
                        await conn.initialize_ftd(intf_obj, ftd_password)

                    asyncio.run(setup())

    #FTD interface configuration
    @aetest.subsection
    def configure_ftd_and_deploy(self, steps):
        """Applies and deploys configuration for FTD"""
        with steps.start("Connect via Swagger", continue_=True) as step:
            if "ftd_interfaces" not in USER_SELECTION:
                step.skipped("User skipped FTD interface configuration")
                return
            for device in self.parent.parameters['tb'].devices:
                if self.tb.devices[device].type != 'ftd':
                    continue
                if "swagger" not in self.tb.devices[device].connections:
                    continue
                conn: SwaggerConnector = self.tb.devices[device].connect(via="swagger")
                self.swagger = conn.get_swagger_client()
                self.connection = conn
                try:
                    conn.accept_eula()
                except bravado.exception.HTTPUnprocessableEntity as e:
                    print('Initial configuration already completed:', e)

            if not self.swagger:
                step.failed("Failed to get Swagger client")

        with steps.start("Delete existing DHCP server", continue_=True) as step: #type: Step
            if "ftd_interfaces" not in USER_SELECTION:
                step.skipped("User skipped Ubuntu Server configuration")
                return
            dhcp_servers = self.swagger.DHCPServerContainer.getDHCPServerContainerList().result()
            for dhcp_server in dhcp_servers['items']:
                dhcp_serv_list = dhcp_server['servers']
                print(dhcp_serv_list)
                dhcp_server.servers = []
                response = self.swagger.DHCPServerContainer.editDHCPServerContainer(
                    objId=dhcp_server.id,
                    body=dhcp_server,
                ).result()
                print(response)

        with steps.start('Configure FTD Interfaces', continue_=True) as step:
            if "ftd_interfaces" not in USER_SELECTION:
                step.skipped("User skipped FTD interface configuration")
                return
            existing_interfaces = self.swagger.Interface.getPhysicalInterfaceList().result()
            csr_ftd_config = self.connection.device.interfaces['csr_ftd']
            ftd_ep2_config = self.connection.device.interfaces['ftd_ep2']

            csr_ftd_swagger = None
            ftd_ep2_swagger = None
            for interface in existing_interfaces['items']:
                if interface.hardwareName == csr_ftd_config.name:
                    csr_ftd_swagger = interface
                if interface.hardwareName == ftd_ep2_config.name:
                    interface = create_ipv4(self.swagger, interface)
                    ftd_ep2_swagger = interface

            if not (csr_ftd_swagger and ftd_ep2_swagger):
                step.failed("Could not find both required interfaces on the FTD.", goto=['exit'])

            csr_ftd_swagger.name = csr_ftd_config.alias
            csr_ftd_swagger.ipv4.ipAddress.ipAddress = csr_ftd_config.ipv4.ip.compressed
            csr_ftd_swagger.ipv4.ipAddress.netmask = csr_ftd_config.ipv4.netmask.exploded
            csr_ftd_swagger.ipv4.dhcp = False
            csr_ftd_swagger.ipv4.ipType = 'STATIC'
            csr_ftd_swagger.enable = True
            csr_ftd_swagger.name = csr_ftd_config.alias
            self.swagger.Interface.editPhysicalInterface(
                objId=csr_ftd_swagger.id, body=csr_ftd_swagger).result()

            ftd_ep2_swagger.name = ftd_ep2_config.alias
            ftd_ep2_swagger.ipv4.ipAddress.ipAddress = ftd_ep2_config.ipv4.ip.compressed
            ftd_ep2_swagger.ipv4.ipAddress.netmask = ftd_ep2_config.ipv4.netmask.exploded
            ftd_ep2_swagger.ipv4.dhcp = False
            ftd_ep2_swagger.ipv4.ipType = 'STATIC'
            ftd_ep2_swagger.name = ftd_ep2_config.alias
            ftd_ep2_swagger.securityLevel = 100
            ftd_ep2_swagger.managementOnly = False
            ftd_ep2_swagger.enable = True
            ftd_ep2_swagger.enabled = True
            self.swagger.Interface.editPhysicalInterface(
                objId=ftd_ep2_swagger.id, body=ftd_ep2_swagger).result()

            interface_for_dhcp = ftd_ep2_swagger
            print(response)

            # Store for later steps
            self.csr_ftd_swagger = csr_ftd_swagger
            self.ftd_ep2_swagger = ftd_ep2_swagger
            step.passed("Successfully configured IP addresses on interfaces.")

        with steps.start("Add DHCP server to interface", continue_=True) as step:
            if "ftd_interfaces" not in USER_SELECTION:
                step.skipped("User skipped Ftd interface configuration")
                return
            dhcp_servers = self.swagger.DHCPServerContainer.getDHCPServerContainerList().result()
            for dhcp_server in dhcp_servers['items']:
                dhcp_serv_list = dhcp_server['servers']
                print(dhcp_serv_list)
                dhcp_server_model = self.swagger.get_model('DHCPServer')
                interface_ref_model = self.swagger.get_model('ReferenceModel')

                dhcp_server.servers = [
                    dhcp_server_model(
                        addressPool='192.168.250.100-192.168.250.200',
                        enableDHCP=True,
                        interface=interface_ref_model(
                            id=interface_for_dhcp.id,
                            name=interface_for_dhcp.name,
                            type='physicalinterface',
                        ),
                        type='dhcpserver'
                    )
                ]
                response = self.swagger.DHCPServerContainer.editDHCPServerContainer(
                    objId=dhcp_server.id,
                    body=dhcp_server,
                ).result()
                print(response)


        # --- Step 3: Create Security Zones with Interface Assignments ---
        with steps.start("Create Security Zones and Assign Interfaces", continue_=True) as step:
            if "ftd_interfaces" not in USER_SELECTION:
                step.skipped("User skipped FTD interface configuration")
                return

            security_zone=self.swagger.SecurityZone.addSecurityZone
            inside_zone_body = {
                "name": "Inside-Zone", "mode": "ROUTED", "type": "securityzone",
                "interfaces": [{"type": "physicalinterface",
                                "id": self.csr_ftd_swagger.id,
                                "name": self.csr_ftd_swagger.name}]
            }
            self.inside_zone = security_zone(body=inside_zone_body).result()

            outside_zone_body = {
                "name": "Outside-Zone", "mode": "ROUTED", "type": "securityzone",
                "interfaces": [{"type": "physicalinterface",
                                "id": self.ftd_ep2_swagger.id,
                                "name": self.ftd_ep2_swagger.name}]
            }
            self.outside_zone = security_zone(body=outside_zone_body).result()
            step.passed("Created zones and assigned interfaces")

        #Static FTD routes
        with steps.start("Add routes", continue_=True) as step:
            if "ftd_interfaces" not in USER_SELECTION:
                step.skipped("User skipped FTD route configuration")
                return

            system_info = self.swagger.SystemInformation.getSystemInformation(
                objId="default"
            ).result()
            device_id = system_info.id
            print(f"Found Device ID (parentId): {device_id}")

            csr_ftd = conn.device.interfaces['csr_ftd']
            #ftd_ep2 = conn.device.interfaces['ftd_ep2']
            existing_interfaces = self.swagger.Interface.getPhysicalInterfaceList().result()

            csr_ftd_swagger = None
            #ftd_ep2_swagger = None

            for interface in existing_interfaces['items']:
                if interface.hardwareName == csr_ftd.name:
                    csr_ftd_swagger = interface
                # if interface.hardwareName == ftd_ep2.name:
                #     ftd_ep2_swagger = interface

            def create_network_object(name, cidr):
                """# Helper: create a network object for a subnet"""
                obj = {
                    "name": name,
                    "value": cidr,
                    "subType": "NETWORK",
                    "type": "networkobject"
                }
                return self.swagger.NetworkObject.addNetworkObject(body=obj).result()

            def create_host_object(name, ip):
                """Helper: create a host object for a gateway IP"""
                obj = {
                    "name": name,
                    "value": ip,
                    "subType": "HOST",
                    "type": "networkobject"
                }
                return self.swagger.NetworkObject.addNetworkObject(body=obj).result()

            routes_to_add = []

            # Route guest1 network
            if csr_ftd_swagger:
                net_obj = create_network_object("net_guest2", "192.168.210.0/24")
                gw_obj = create_host_object("gw_guest2", "192.168.240.4")

                routes_to_add.append({
                    "name": "route_to_guest1",
                    "iface": {
                        "id": csr_ftd_swagger.id,
                        "name": csr_ftd_swagger.name,
                        "type": "physicalinterface"
                    },
                    "networks": [{
                        "id": net_obj["id"],
                        "name": net_obj["name"],
                        "type": net_obj["type"]
                    }],
                    "gateway": {
                        "id": gw_obj["id"],
                        "name": gw_obj["name"],
                        "type": gw_obj["type"]
                    },
                    "metricValue": 1,
                    "ipType": "IPv4",
                    "type": "staticrouteentry"
                })

                # Route: IOU/IOSv subnet
                net_obj = create_network_object("ftd_iou_iosv", "192.168.220.0/24")
                gw_obj = create_host_object("gw_iou_iosv", "192.168.240.4")

                routes_to_add.append({
                    "name": "route_to_iou_iosv",
                    "iface": {
                        "id": csr_ftd_swagger.id,
                        "name": csr_ftd_swagger.name,
                        "type": "physicalinterface"
                    },
                    "networks": [{
                        "id": net_obj["id"],
                        "name": net_obj["name"],
                        "type": net_obj["type"]
                    }],
                    "gateway": {
                        "id": gw_obj["id"],
                        "name": gw_obj["name"],
                        "type": gw_obj["type"]
                    },
                    "metricValue": 1,
                    "ipType": "IPv4",
                    "type": "staticrouteentry"
                })

                # Route to IOSv-CSR subnet
                net_obj = create_network_object("ftd_iosv_csr", "192.168.230.0/24")
                gw_obj = create_host_object("gw_iosv_csr", "192.168.240.4")

                routes_to_add.append({
                    "name": "route_to_iosv_csr",
                    "iface": {
                        "id": csr_ftd_swagger.id,
                        "name": csr_ftd_swagger.name,
                        "type": "physicalinterface"
                    },
                    "networks": [{
                        "id": net_obj["id"],
                        "name": net_obj["name"],
                        "type": net_obj["type"]
                    }],
                    "gateway": {
                        "id": gw_obj["id"],
                        "name": gw_obj["name"],
                        "type": gw_obj["type"]
                    },
                    "metricValue": 1,
                    "ipType": "IPv4",
                    "type": "staticrouteentry"
                })

            if routes_to_add:
                for route in routes_to_add:
                    print(f"Adding static route '{route['name']}'...")
                    response = self.swagger.Routing.addStaticRouteEntry(
                        parentId=device_id,
                        body=route
                    ).result()
                    print("Added static route:", response)
            else:
                print("No static routes to add")

        with steps.start("Add Access Control Rules", continue_=True) as step:
            if "ftd_interfaces" not in USER_SELECTION:
                step.skipped("User skipped FTD interface configuration")
                return

            policy_id = self.swagger.AccessPolicy.getAccessPolicyList().result()['items'][0].id

            rule1_body = {
                "name": "Allow_Inside_to_Outside",
                "action": "PERMIT",
                "enabled": True,
                "type": "accessrule",
                "sourceZones": [{"id": self.inside_zone.id, "type": "securityzone"}],
                "destinationZones": [{"id": self.outside_zone.id, "type": "securityzone"}]
            }
            self.swagger.AccessPolicy.addAccessRule(parentId=policy_id, body=rule1_body).result()

            rule2_body = {
                "name": "Allow_Outside_to_Inside",
                "action": "PERMIT",
                "enabled": True,
                "type": "accessrule",
                "sourceZones": [{"id": self.outside_zone.id, "type": "securityzone"}],
                "destinationZones": [{"id": self.inside_zone.id, "type": "securityzone"}]
            }
            self.swagger.AccessPolicy.addAccessRule(parentId=policy_id, body=rule2_body).result()
            step.passed("Successfully created bidirectional access rules.")

        with steps.start("Deploy Pending Changes", continue_=True) as step:
            if "ftd_interfaces" not in USER_SELECTION:
                step.skipped("User skipped FTD interface configuration")
                return
            deployment_request = {"type": "deploymentrequest", "forceDeploy": True}
            task = self.swagger.Deployment.addDeployment(body=deployment_request).result()
            print("Deploying, please wait")
            time.sleep(50)
            step.passed("Deployment complete.")

    @aetest.subsection
    def bad_csr_config(self, steps):
        """DEBUG Subsection:
        Applies bad configuration on CSR so it can be diagnosed"""
        for device in self.tb.devices:
            if self.tb.devices[device].alias != 'csr':
                continue
            with steps.start(f'Bad {device} config', continue_=True) as step: #type: Step
                if "bad_csr_config" not in USER_SELECTION:
                    step.skipped("User skipped Ubuntu Server configuration")
                    return

                bad_intf_commands=[]

                for interface in self.tb.devices[device].interfaces:
                    intf_obj=self.tb.devices[device].interfaces[interface]
                    if intf_obj.type == "management":
                        continue

                    conn_class=self.tb.devices[device].connections.get('telnet',{}).get('class')
                    assert conn_class,f'No connection for device {device}'
                    ip = self.tb.devices[device].connections.telnet.ip.compressed
                    port = self.tb.devices[device].connections.telnet.port

                    correct_subnet = intf_obj.ipv4.network.network_address
                    correct_subnet_third_byte = correct_subnet.compressed.split('.')[2]
                    bad_subnet_third_byte=str(int(correct_subnet_third_byte)+5)

                    bad_intf_ip= IPv4Address("192.168."+bad_subnet_third_byte+".50")
                    print(bad_intf_ip)

                    commands=bad_csr_commands.bad_interface_commands
                    bad_intf_commands+=list(map(
                        lambda s: s.format(
                            interface=interface,
                            ip=bad_intf_ip.compressed,
                            sm=intf_obj.ipv4.netmask.exploded,
                        ),
                        commands
                    ))

                bad_route_config=bad_csr_commands.bad_route_commands
                print(bad_route_config)
                conn: TelnetConnection = conn_class(ip, port)
                formatted_commands=bad_intf_commands + bad_route_config
                print(formatted_commands)

                async def setup():
                    await conn.connect()
                    time.sleep(1)
                    await conn.enable_csr()
                    await conn.enter_commands(formatted_commands, '#')
                asyncio.run(setup())

    @aetest.subsection
    def verify_guest_connectivity(self, steps):
        """Pings Guest2 PC from Guest1 and offers the possibility for diagnostics if ping fails"""
        global USER_SELECTION

        with steps.start("Pinging from end devices via Telnet") as step:
            if "ping_end_devices" not in USER_SELECTION:
                step.skipped("User skipped FTD interface configuration")
                return

            # Get the device objects from the testbed
            source_guest = self.tb.devices['UbuntuDockerGuest-1']
            dest_guest = self.tb.devices['UbuntuDockerGuest-2']
            destination_ip = dest_guest.custom['ping_ip']

            ping_success=False

            conn_class=source_guest.connections.get('telnet',{}).get('class',None)
            assert conn_class,f'No connection for device {source_guest}'
            ip = source_guest.connections.telnet.ip.compressed
            port = source_guest.connections.telnet.port

            conn: TelnetConnection = conn_class(ip, port)

            async def setup():
                nonlocal ping_success
                await conn.connect()
                time.sleep(1)
                ping_success = await conn.ping_end_device(destination_ip)
            asyncio.run(setup())

            if ping_success:
                step.passed(f"Successfully pinged {destination_ip}. No diagnose needed")
            else:
                print(f"Failed to ping {destination_ip}.")
                diag_opt=input("Would you like to start diagnose process? [y/n]: ").lower()
                if diag_opt == "n":
                    step.skipped("User skipped FTD interface configuration")
                    return
                if diag_opt == "y":
                    print("Starting diagnose process")
                    if "diagnose" not in USER_SELECTION:
                        USER_SELECTION.add("diagnose")

    @aetest.subsection
    def self_diagnose_csr(self, steps):
        """Self diagnoses CSR to see if any bad configuration was applied"""
        with steps.start("Diagnose CSR", continue_=True) as step: #type: Step
            if "diagnose" not in USER_SELECTION:
                step.skipped("User skipped CSR Diagnose")
                return

            # --- Step 1: Get the device object and connect ---
            csr_obj=self.tb.devices['CSR']
            conn_class=csr_obj.connections.get('telnet',{}).get('class',None)
            assert conn_class,f'No connection for device {csr_obj}'
            ip = csr_obj.connections.telnet.ip.compressed
            port = csr_obj.connections.telnet.port

            conn: TelnetConnection = conn_class(ip, port)

            iosv_intf = None
            ftd_intf = None

            #Get information from other devices
            for device in self.tb.devices:
                if self.tb.devices[device].type not in ['router', 'ftd']:
                    continue
                if device == csr_obj:
                    continue
                # get only neighboring interfaces
                for interface in self.tb.devices[device].interfaces:
                    intf_alias=self.tb.devices[device].interfaces[interface].link.alias
                    if self.tb.devices[device].interfaces[interface].link.name == 'management':
                        continue
                    if 'csr' in intf_alias.split('_')[1]:
                        iosv_intf=self.tb.devices[device].interfaces[interface]
                    if 'csr' in intf_alias.split('_')[0]:
                        ftd_intf=self.tb.devices[device].interfaces[interface]

            fixes_applied = False

            async def setup():
                nonlocal fixes_applied
                await conn.connect()
                time.sleep(1)
                await conn.enable_csr()

                try:
                    intf_lines=[]
                    while len(intf_lines)<2:
                        csr_interfaces_raw = await conn.get_response('show ip int br')
                        intf_lines = csr_interfaces_raw.splitlines()

                    parsed_routes_raw = await conn.get_response('show run | i ip route')
                    route_lines = parsed_routes_raw.splitlines()
                except Exception as e:
                    step.failed(f"Failed to parse configuration from CSR: {e}")
                    return

                commands_to_fix = []

                actual_interface_ips = {}
                for line in intf_lines:
                    parts = line.split()
                    if len(parts) > 2 and parts[1][0].isdigit():
                        actual_interface_ips[parts[0]] = parts[1]

                print(f"Found live interface IPs: {actual_interface_ips}")

                print("Diagnosing interface configurations...")
                interfaces_to_check = {
                    'GigabitEthernet2': iosv_intf,
                    'GigabitEthernet3': ftd_intf
                }

                for intf_name, peer_intf_config in interfaces_to_check.items():
                    intd_csr_ipv4 = csr_obj.interfaces[intf_name].ipv4
                    peer_ipv4 = peer_intf_config.ipv4

                    if intd_csr_ipv4.network != peer_ipv4.network:
                        print(
                            f"TESTBED MISCONFIGURATION on link for {intf_name}. "
                            f"CSR is on {intd_csr_ipv4.network} but peer is on {peer_ipv4.network}."
                        )

                    if actual_interface_ips.get(intf_name) != str(intd_csr_ipv4.ip):
                        print(f"IP MISMATCH on {intf_name}. Generating fix.")
                        commands_to_fix.extend([
                            f'interface {intf_name}',
                            f'ip address {intd_csr_ipv4.ip} {intd_csr_ipv4.netmask}',
                            'no shutdown'
                        ])

                actual_static_routes_list = []
                for line in route_lines:
                    parts = line.split()
                    if len(parts) >= 5 and parts[0] == 'ip' and parts[1] == 'route':
                        # ip route <network> <mask> <gateway> [other_params...]
                        network, mask, gateway = parts[2], parts[3], parts[4]
                        actual_static_routes_list.append({
                            "network": network,
                            "mask": mask,
                            "gateway": gateway
                        })

                print(f"Found live static routes: {actual_static_routes_list}")
                print("Diagnosing static routes...")
                expected_routes = [
                    {
                        'network': '192.168.210.0',
                        'mask': '255.255.255.0',
                        'gateway': '192.168.230.3'
                    },
                    {
                        'network': '192.168.220.0',
                        'mask': '255.255.255.0',
                        'gateway': '192.168.230.3'
                    },
                    {
                        'network': '192.168.250.0',
                        'mask': '255.255.255.0',
                        'gateway': '192.168.240.5'
                    },
                ]

                print("Diagnosing static routes...")

                routes_to_remove = [
                    f"no ip route {route['network']} {route['mask']} {route['gateway']}"
                    for route in actual_static_routes_list
                    if route not in expected_routes
                ]
                if routes_to_remove:
                    print(f"Found incorrect routes to remove: {routes_to_remove}")

                routes_to_add = [
                    f"ip route {route['network']} {route['mask']} {route['gateway']}"
                    for route in expected_routes
                    if route not in actual_static_routes_list
                ]
                if routes_to_add:
                    print(f"Found missing routes to add: {routes_to_add}")

                commands_to_fix.extend(routes_to_remove)
                commands_to_fix.extend(routes_to_add)

                if commands_to_fix:
                    fixes_applied = True
                    print(f"Found configuration issues. Applying {len(commands_to_fix)} fixes...")

                    config_session_commands = ['conf t'] + commands_to_fix + ['end']

                    await conn.enter_commands(config_session_commands, '#')
                    print("Successfully applied configuration fixes.")
                else:
                    print("No configuration issues found on CSR.")

            asyncio.run(setup())

            if fixes_applied:
                step.passed("Completed diagnose process and applied fixes.")
            else:
                step.passed("No configuration issues were found on CSR")

if __name__ == "__main__":
    OPT=True
    while OPT:
        USER_SELECTION = get_user_options()
        print(f"\nSelected: {USER_SELECTION}\n")
        aetest.main()
        while True:
            opt_input=input("Do you want to continue configuration? [y/n]: ")
            #opt_input="n"
            if opt_input in ('y', 'yes'):
                OPT=True
                break
            if opt_input in ('n', 'no'):
                OPT=False
                break
            print("Please enter yes or no")
            continue
