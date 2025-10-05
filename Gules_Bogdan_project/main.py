"""
Main module for Gules_Bogdan_project.

This script loads a testbed from a YAML file, configures Ubuntu servers,
routers, and FTD devices via telnet/SSH/Swagger API, and provides
a menu for diagnostics and device configuration.

Author: Gules Bogdan
"""

import asyncio
import ipaddress
import subprocess
import time
import telnetlib3
import paramiko
import yaml
import ssh
import urllib3

from Gules_Bogdan_project.swagger import SwaggerConnector

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)



#---------------------------------------------LOAD TESTBED-------------------------------------

def load_testbed(path='devices.yaml'):
    """Load the network testbed from a YAML file and return it as a dictionary."""
    with open(path, encoding='utf-8') as f:
        return yaml.safe_load(f)
#-------------------------------------------UBUNTU CONFIG--------------------------------------
def configure_ubuntu():
    """Configure Ubuntu server interfaces and routing based on the testbed."""
    testbed = load_testbed()
    server = testbed['topology']['UbuntuServer']
    ubuntu_subnets = []
    for interface_name, interface_prop in server['interfaces'].items():
        ip = interface_prop['ipv4']
        print(f"Interface: {interface_name}, IP: {ip}")
        result = subprocess.run(['ip', 'addr', 'show', interface_name],
                                capture_output=True, text=True, check=True)
                                #rezult.stdout               string      checks for errors
        if ip.split('/')[0] not in result.stdout :
            subprocess.run(['sudo', 'ip', 'addr', 'add', ip, 'dev', interface_name
                            ], check=True)
            subprocess.run(['sudo', 'ip', 'link', 'set', 'dev', interface_name, 'up'
                            ], check=True)

            print(f"Interface: {interface_name}, IP: {ip} configurate")
        else:
            print(f"{ip} is already on {interface_name}")

        ubuntu_subnets.append(ipaddress.IPv4Network(ip, strict=False))

    #-----------------------------------------------routes---------------------------------------

    ubuntu_ip = list(server['interfaces'].values())[0]['ipv4'].split('/')[0]
    ubuntu_networks = [ipaddress.IPv4Network(f"{ubuntu_ip}/24", strict=False)]
                    #convert a string into  ipv4 network object
    for device_name, device_data in testbed['topology'].items():
        if device_name == 'UbuntuServer':
            continue

        mgmt_ip = None
        routes = []

        for _, iface_data in device_data.get('interfaces', {}).items():
            ip_with_mask = iface_data.get('ipv4')
            if not ip_with_mask:
                continue


            ip_str = ip_with_mask.replace(" ", "/")
            if "/" not in ip_str:
                ip_str += "/24"

            ip = ip_str.split('/')[0]
            network = ipaddress.IPv4Network(ip_str, strict=False)
            #change 192.168.200.2/255.255.255.0 into 192.168.200.2/24

            if ipaddress.ip_address(ip) in ipaddress.ip_network("192.168.200.0/24"):
                mgmt_ip = ip
                continue

            if any(network.overlaps(subnet) for subnet in ubuntu_networks):
                continue

            routes.append(network)

        if mgmt_ip:
            for net in routes:
                result = subprocess.run(['ip', 'route', 'show', str(net)]
                                        , capture_output=True, text=True, check=True)
                if str(net) in result.stdout:
                    print(f"Route {net} already exists, skipping.")
                    continue

                subprocess.run(['sudo', 'ip', 'route', 'add', str(net), 'via', mgmt_ip
                                ], check=True)
                print(f"Route {net} added via {mgmt_ip}")
#-------------------------------------------------FTD CONSOLE INITIALIZATION-------------------

async def initialize_ftd_console(ftd_conn, ftd_topo):
    """Initialize FTD device via telnet console for first-time setup."""
    host = '92.81.55.146'
    port = ftd_conn['connections']['telnet']['port']
    ip = ftd_conn['connections']['telnet']['ip']
    password = ftd_conn['credentials']['default']['password']

    reader, writer = await telnetlib3.open_connection(host, port)
    print("Connected to FTD console")

    buffer = ""
    writer.write("\n")

    while True:
        chunk = await reader.read(1000)
        if not chunk:
            await asyncio.sleep(1)
            continue

        buffer += chunk
        print("CLI:", chunk)


        if "firepower login:" in buffer:
            writer.write("admin\n")
            await writer.drain() #wait for the buffer to be empty,
                                # meaning the data is actually transferred.
            buffer = ""

        elif "Password:" in buffer and "Enter new password:" not in buffer:
            writer.write("Admin123\n")
            await writer.drain()
            buffer = ""


        elif "Press <ENTER> to display the EULA:" in buffer:
            writer.write("\n")
            await writer.drain()
            buffer = ""

        elif "--More--" in buffer:
            writer.write(" ")
            await writer.drain()
            buffer = ""

        elif "Please enter 'YES' or press <ENTER> to AGREE to the EULA:" in buffer:
            writer.write("\n")
            await writer.drain()
            buffer = ""


        elif "Enter new password:" in buffer:
            writer.write(f"{password}\n")
            await writer.drain()
            buffer = ""

        elif "Confirm new password:" in buffer:
            writer.write(f"{password}\n")
            await writer.drain()
            buffer = ""


        elif "Do you want to configure IPv4? (y/n) [y]:" in buffer:
            writer.write("\n")
            await writer.drain()
            buffer = ""

        elif "Do you want to configure IPv6? (y/n) [n]:" in buffer:
            writer.write("\n")
            await writer.drain()
            buffer = ""

        elif "Configure IPv4 via DHCP or manually? (dhcp/manual) [manual]:" in buffer:
            writer.write("manual\n")
            await writer.drain()
            buffer = ""

        elif "Enter an IPv4 address for the management interface" in buffer:
            writer.write(f"{ip}\n")
            await writer.drain()
            buffer = ""

        elif "Enter an IPv4 netmask for the management interface" in buffer:
            writer.write("255.255.255.0\n")
            await writer.drain()
            buffer = ""

        elif "Enter a fully qualified hostname for this system [firepower]:" in buffer:
            writer.write("\n")
            await writer.drain()
            buffer = ""

        elif "Enter the IPv4 default gateway for the management interface" in buffer:
            writer.write("192.168.200.6\n")
            await writer.drain()
            buffer = ""

        elif "Enter a comma-separated list of DNS servers" in buffer:
            writer.write("\n")
            await writer.drain()
            buffer = ""

        elif "Enter a comma-separated list of search domains" in buffer:
            writer.write("\n")
            await writer.drain()
            buffer = ""

        elif "Manage the device locally? (yes/no) [yes]:" in buffer:
            writer.write("\n")
            await writer.drain()
            buffer = ""


        elif buffer.strip().endswith(">"):
            print("FTD initial setup completed via console")
            break

    writer.close()

#-------------------------------------------ROUTERS CONFIG-------------------------------------

async def configure_routers(router_name, router_conn, router_topo):
    """Configure router interfaces, RIP, and SSH based on testbed topology."""
    host = '92.81.55.146'
    port = router_conn['connections']['telnet']['port']
    hostname= router_name
    username = router_conn['credentials']['default']['username']
    password = router_conn['credentials']['default']['password']
    pass_secret=router_conn['credentials']['enable']['password']

    reader, writer = await telnetlib3.open_connection(host, port)
    print(f"Connected to {router_name}")
    output = await reader.read(1024)
    print(output, "First")
    buffer = ""
    while True:
        chunk = await reader.read(1024)
        buffer += chunk


        if "Press RETURN to get started!" in buffer:
            writer.write("\r\n")
            await writer.drain()
            buffer = ""


        if router_name == 'CSR':
            if "Would you like to enter the initial configuration dialog? [yes/no]:" in buffer:
                writer.write("no\n")
                await writer.drain()
                buffer = ""
            elif "Would you like to terminate autoinstall? [yes]:" in buffer:
                writer.write("\n")
                await writer.drain()
                buffer = ""
            elif "Guestshell destroyed successfully stall? [yes]:" in buffer:
                writer.write("\n")
                await writer.drain()
                buffer = ""
                print(buffer,"Middle-----------------")
            elif "--More--" in buffer:
                writer.write(" ")
                await writer.drain()
                buffer = ""
            elif "Guestshell destroyed successfully" in buffer:
                writer.write("\n")
                await writer.drain()
                await asyncio.sleep(0.5)
                writer.write("\n")
                await writer.drain()
                buffer = ""
            elif "Router>" in buffer:
                print("CSR prompt detected")
                writer.write("\n")
                await writer.drain()
                buffer = ""
                break

        # IOU / IOSv
        else:
            if buffer.strip().endswith("#") or buffer.strip().endswith(">"):
                print(f"{router_name} prompt detected")
                writer.write("\n")
                await writer.drain()
                buffer = ""
                break

        await asyncio.sleep(0.5)

    writer.write('\n')
    output = await reader.read(1024)
    print(output,"Second")

    await asyncio.sleep(0.5)
    writer.write('\n')
    output = await reader.read(1024)
    await asyncio.sleep(0.5)
    writer.write("enable\n")
    print(output)
    if "Password" in output:
        writer.write(router_conn['credentials']['enable']['password'] + '\n')
        await writer.drain()
        await asyncio.sleep(0.5)

    writer.write("configure terminal\n")
    await asyncio.sleep(0.5)
    writer.write(f"hostname {router_name}\n")
    await asyncio.sleep(0.5)

    # === configure interfaces ===
    for intf, data in router_topo['interfaces'].items():
        writer.write(f"interface {intf}\n")
        if 'ipv4' in data and data['ipv4']:
            writer.write(f"ip address {data['ipv4']}\n")
        writer.write("no shutdown\n")
        writer.write("exit\n")
        await asyncio.sleep(0.5)

        # === configure RIP ===
    def extract_networks(topo):
        nets = set()
        for intf, data in topo.get("interfaces", {}).items():
            ipv4 = data.get("ipv4")
            if not ipv4:
                continue
            s = str(ipv4).strip()
            try:
                if "/" in s:
                    iface = ipaddress.ip_interface(s)
                    net = iface.network
                else:
                    ip, mask = s.split()
                    net = ipaddress.ip_network(f"{ip}/{mask}", strict=False)
                # without 192.168.200.0 for RIP
                if str(net.network_address).startswith("192.168.200."):
                    continue
                nets.add(net.network_address.exploded)
            except Exception as e:
                print(f"[{router_name}] Skipping {ipv4}: {e}")
        return sorted(nets)

    rip_networks = extract_networks(router_topo)
    if rip_networks:
        writer.write("router rip\n")
        await asyncio.sleep(0.3)
        writer.write("version 2\n")
        await asyncio.sleep(0.3)
        writer.write("no auto-summary\n")
        await asyncio.sleep(0.3)
        for net in rip_networks:
            writer.write(f"network {net}\n")
            await asyncio.sleep(0.3)
        writer.write("exit\n")
        await asyncio.sleep(0.3)
        print(f"[{router_name}] RIP configured for: {', '.join(rip_networks)}")
    else:
        print(f"[{router_name}] No networks found for RIP")

    # === configure SSH ===
    for cmd in ssh.commands:
        writer.write(cmd.format(
            hostname=hostname,
            username=username,
            password=password,
            pass_secret=pass_secret
        ) + '\n')
        await asyncio.sleep(0.5)
        output = await reader.read(1024)
        print(output, end="")

    writer.write("end\n")
    await asyncio.sleep(0.5)
    output = await reader.read(1024)
    print(output,"Final")
    writer.write("write memory\n")
    await asyncio.sleep(0.5)
    output = await reader.read(1024)
    print(output, "Write memory")
    if router_name in ('IOSv', 'IOS'):
        output = await reader.read(1024)
        if "Overwrite the previous NVRAM configuration" in output:
            writer.write("\n")
            await asyncio.sleep(0.5)
    output = await reader.read(1024)
    print(output,"Configuration complete")
    writer.close()

#-------------------------------------------FTD CONFIG (Swagger API)---------------------------

def delete_existing_dhcp(swagger_client):
    """Delete all DHCP server entries via Swagger API."""
    try:
        dhcp_containers_resp = (swagger_client.DHCPServerContainer
                                .getDHCPServerContainerList().result())
        dhcp_containers = dhcp_containers_resp.items  # use .items, not .get()

        for container in dhcp_containers:
            print(f"Clearing DHCP servers in container: {container.name}")

            # Fetch full container object
            container_obj = swagger_client.DHCPServerContainer.getDHCPServerContainer(
                objId=container.id).result()

            # Clear servers
            container_obj.servers = []

            # Update container
            response = swagger_client.DHCPServerContainer.editDHCPServerContainer(
                objId=container_obj.id,
                body=container_obj
            ).result()
            print(f"Cleared DHCP container {container.name}: {response}")

    except Exception as e:
        print(f"Failed to delete existing DHCP servers: {e}")

def configure_ftd(ftd_conn, ftd_topo):
    """Configure FTD device via console and Swagger API."""
    if 'telnet' in ftd_conn['connections']:
        asyncio.run(initialize_ftd_console(ftd_conn, ftd_topo))


    configure_ubuntu()
    connection = SwaggerConnector(ftd_conn).connect()
    if not connection:
        print("Could not connect via Swagger API")
        return
    print("Sleep 300 seconds")
    time.sleep(300)
    swagger = connection.get_swagger_client()
    print(dir(swagger))
    if not swagger:
        print("No swagger client")
        return
    connection.accept_eula()
    existing_interfaces = swagger.Interface.getPhysicalInterfaceList().result()
    allowed_interfaces = ["GigabitEthernet0/0", "GigabitEthernet0/1"]

    delete_existing_dhcp(swagger)
    add_static_routes_and_rule(swagger, ftd_topo)

    for intf_name, intf_data in ftd_topo.get('interfaces', {}).items():
        if intf_name not in allowed_interfaces:
            continue
        if 'ipv4' not in intf_data or not intf_data['ipv4']:
            continue
        ip, netmask = intf_data['ipv4'].split()

        for iface in existing_interfaces['items']:

            if iface.hardwareName == intf_name:

                iface = swagger.Interface.getPhysicalInterface(objId=iface.id).result()

                ha_ipv4_address = swagger.get_model("HAIPv4Address")
                interface_ipv4 = swagger.get_model("InterfaceIPv4")

                ip_addr_obj = ha_ipv4_address(ipAddress=ip, netmask=netmask, type="haipv4address")
                ipv4_obj = interface_ipv4(
                    ipAddress=ip_addr_obj,
                    ipType="STATIC",
                    type="interfaceipv4"
                )

                iface.dhcp = False
                iface.ipv4 = ipv4_obj
                iface.enable = True
                iface.enabled = True
                iface.monitorInterface = True
                iface.mode = "ROUTED"
                alias = intf_data.get("alias", intf_name.lower().replace("/", "_"))
                iface.name = alias

                try:
                    response = (swagger.Interface.editPhysicalInterface
                                (objId=iface.id, body=iface._as_dict()).result())
                    print(f"Configured {intf_name} as {alias}: {response}")

                except Exception as e:
                    print(f"Failed to configure {intf_name}: {e}")

    # --- Deployment ---
    try:
        deployment_body = {
            "type": "deployment",
            "forceDeploy": True,
            "version": ftd_conn.get("version", "7.7.0")
        }
        deployment_response = swagger.Deployment.addDeployment(
            body=deployment_body).result()
        deployment_id = getattr(
            deployment_response, "id", None)
        print(f"Deployment queued - ID: {deployment_id}, "
              f"State: {getattr(deployment_response, 'state', '')}")

        # Polling deployment status
        timeout = 300  # 5 minute
        poll_interval = 5
        start_time = time.time()

        while True:
            deployment_status = swagger.Deployment.getDeployment(objId=deployment_id).result()
            state = getattr(deployment_status, "state", "")
            print("Deployment status:", state)

            if state == "DEPLOYED":
                print("Deployment completed successfully")
                break
            if state in ["FAILED", "ERROR"]:
                print("Deployment failed")
                break

            if time.time() - start_time > timeout:
                print("Deployment timed out")
                break

            messages = getattr(deployment_status, "deploymentStatusMessages", [])
            if messages:
                last_task = messages[-1]
                print(f"Task: {last_task.taskName}, State: {last_task.taskState}")

            time.sleep(poll_interval)

    except Exception as e:
        print("Failed to create/apply deployment:", e)

#--------------------------------------------STATIC ROUTES_____________________________________
def add_static_routes_and_rule(swagger, topo, ftd_device_name='FTD'):
    """
    Add a permit access rule and static routes for traffic on FTD.
    """
    try:
        # --- Access Rule ---
        access_policy  = swagger.AccessPolicy
        access_rule = swagger.get_model('AccessRule')
        policies = access_policy.getAccessPolicyList().result()
        if policies.items:
            policy_id = policies.items[0].id

            rules = access_policy.getAccessRuleList(parentId=policy_id).result().items
            if any(r.name == "PermitAllStaticRoutes" for r in rules):
                print("Access Rule 'PermitAllStaticRoutes' already exists, skipping creation")
            else:
                rule = access_rule(
                    name='PermitAllStaticRoutes',
                    ruleAction='PERMIT',
                )
                res = access_policy.addAccessRule(parentId=policy_id, body=rule).result()
                print("Access Rule created:", res)
        else:
            print("No access policies found, cannot create rule")

        # --- Add static routes ---
        add_static_routes(swagger, topo, ftd_device_name)

    except Exception as e:
        print("Failed to add static routes and access rule:", e)

def add_static_routes(swagger, topo, ftd_device_name='FTD'):
    """
    Add static routes to the FTD device using Swagger API based on topology.
    Ensures VRF, interfaces, and network objects exist.
    """
    try:
        vrfs_resp = swagger.Routing.getVirtualRouterList().result()
        vrfs = getattr(vrfs_resp, 'items', [])
        if not vrfs:
            print("No VRFs found, cannot add static routes")
            return

        vrf = vrfs[0]
        print(f"Using VRF: {vrf.name} (ID: {vrf.id})")

        ftd_interfaces = {i.hardwareName: i for i in swagger.
        Interface.getPhysicalInterfaceList().result().items}

        network_objects_resp = swagger.NetworkObject.getNetworkObjectList().result()
        network_objects = {n.name: n for n in network_objects_resp.items}

        ftd_topo_intfs = topo.get(ftd_device_name, {}).get('interfaces', {})
        for intf_name, intf_data in ftd_topo_intfs.items():
            ip_cidr = intf_data.get('ipv4')
            if not ip_cidr:
                continue

            if intf_name == "GigabitEthernet0/0":
                gateway_ip = "192.168.204.0"
                dest_networks = ["192.168.204.0/24"]
            elif intf_name == "GigabitEthernet0/1":
                gateway_ip = "192.168.207.0"
                dest_networks = ["192.168.207.0/24"]
            else:
                continue

            reference_model = swagger.get_model('ReferenceModel')
            static_route_entry = swagger.get_model('StaticRouteEntry')
            network_object= swagger.get_model('NetworkObject')

            for dest_net in dest_networks:
                if dest_net not in network_objects:
                    obj = network_object(
                        name=dest_net,
                        value=dest_net,
                        type="networkobject"
                    )
                    try:
                        network_obj_resp = swagger.NetworkObject.addNetworkObject(body=obj).result()
                        network_objects[dest_net] = network_obj_resp
                        print(f"Created network object: {dest_net}")
                    except Exception as e:
                        print(f"Failed to create network object {dest_net}: {e}")
                        continue

                iface_obj = ftd_interfaces.get(intf_name)
                if not iface_obj:
                    print(f"Interface {intf_name} not found on FTD")
                    continue

                route_model = static_route_entry(
                    gateway=reference_model(type="host", value=gateway_ip),
                    iface=reference_model(
                        id=iface_obj.id,
                        name=iface_obj.name,
                        hardwareName=iface_obj.hardwareName,
                        type=iface_obj.type
                    ),
                    ipType='IPv4',
                    type='staticrouteentry',
                    networks=[reference_model(
                        id=network_objects[dest_net].id,
                        name=network_objects[dest_net].name,
                        type=network_objects[dest_net].type
                    )]
                )

                try:
                    swagger.Routing.addStaticRouteEntry(parentId=vrf.id, body=route_model).result()
                    print(f"Static route added: {dest_net} via {gateway_ip} on {intf_name}")
                except Exception as e:
                    print(f"Failed to add static route {dest_net}: {e}")

        # Deploy changes
        try:
            deployment_resp = swagger.Deployment.addDeployment().result()
            deployment_id = getattr(deployment_resp, 'id', None)
            print(f"Deployment queued with ID: {deployment_id}")

            while True:
                deployment_status = swagger.Deployment.getDeployment(objId=deployment_id).result()
                state = getattr(deployment_status, 'state', '')
                if state == "DEPLOYED":
                    print("Static route deployment completed successfully")
                    break
                if state in ["FAILED", "ERROR"]:
                    print("Static route deployment failed")
                    break
                else:
                    messages = getattr(deployment_status, 'deploymentStatusMessages', [])
                    if messages:
                        last_task = messages[-1]
                        print(f"Task: {last_task.taskName}, State: {last_task.taskState}")
                    time.sleep(5)

        except Exception as e:
            print("Failed to deploy static routes:", e)

    except Exception as e:
        print("Failed to add static routes:", e)

#-------------------------------------------MENU-----------------------------------------------

def menu():
    """Main interactive menu with Configure All and Diagnostics options."""
    configure_ubuntu()
    devices_list = [d for d in testbed['devices'].keys() if d != 'UbuntuServer']

    while True:
        print("\nMain Menu:")
        print("1. Configure all devices")
        print("2. Diagnostics (Ping / SSH)")
        print("0. Exit")

        choice = input("Select an option: ")

        if choice == "0":
            print("Exiting...")
            break

        if choice == "1":
            # Configure all devices automatically
            for dev_name in devices_list:
                print(f"\n=== Configuring {dev_name} ===")
                dev_conn = testbed['devices'][dev_name]
                dev_topo = testbed['topology'].get(dev_name, {})

                if dev_name == 'FTD':
                    configure_ftd(dev_conn, dev_topo)
                else:
                    asyncio.run(configure_routers(dev_name, dev_conn, dev_topo))
                print(f"=== {dev_name} configuration completed ===\n")
            print("All devices configured.\n")

        elif choice == "2":
            # Diagnostics menu
            diagnostics_menu(devices_list)

        else:
            print("Invalid selection, please choose again.")


def diagnostics_menu(devices_list):
    """Diagnostics submenu for pinging and SSH commands."""
    while True:
        print("\nDiagnostics Menu:")
        for i, dev in enumerate(devices_list, 1):
            print(f"{i}. Device {dev}")
        print(f"{len(devices_list) + 1}. Ping Guest1 (192.168.201.10)")
        print("0. Back")

        choice = input("Select a device or action: ")
        if choice == "0":
            break
        if choice.isdigit():
            choice = int(choice)
            if 1 <= choice <= len(devices_list):
                dev_name = devices_list[choice - 1]  #because its 0,1,2,3
                print(f"\nDiagnostics for {dev_name}:")
                print("1. Ping device")

                if dev_name != "FTD":
                    print("2. SSH to device and run 'show ip int br'")

                diag_choice = input("Select action: ")

                dev_ip = testbed['devices'][dev_name]['connections']['telnet']['ip']
                username = testbed['devices'][dev_name]['credentials']['default']['username']
                password = testbed['devices'][dev_name]['credentials']['default']['password']

                if diag_choice == "1":
                    ping_device(dev_ip)
                elif diag_choice == "2" and dev_name != "FTD":
                    ssh_show_ip(dev_ip, username, password)
                else:
                    print("Invalid action")
            elif choice == len(devices_list) + 1:
                ping_guest1()
            else:
                print("Invalid selection.")
        else:
            print("Invalid selection.")


def ping_device(ip):
    """Ping a given IP from the Ubuntu server."""
    print(f"Pinging {ip}...")
    try:
        subprocess.run(["ping", "-c", "4", ip
                        ], check=True)
    except subprocess.CalledProcessError:
        print(f"Ping failed to {ip}")

def ssh_show_ip(ip, username, password):
    """Connect via SSH and run 'show ip interface brief'."""
    print(f"Connecting to {ip} via SSH...")
    try:
        ssh1 = paramiko.SSHClient()
        ssh1.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh1.connect(ip, username=username, password=password)
        _, stdout, _= ssh1.exec_command("show ip int br")
        print(stdout.read().decode())
        ssh1.close()
    except paramiko.SSHException as e:
        print(f"SSH connection failed: {e}")
    except (paramiko.AuthenticationException, paramiko.SSHException) as e:
        print(f"Network/Authentication error: {e}")

def ping_guest1():
    """Ping the Guest1 machine (192.168.201.10)."""
    guest_ip = "192.168.201.10"
    print(f"Pinging Guest1 at {guest_ip}...")
    try:
        subprocess.run(["ping", "-c", "4", guest_ip], check=True)
    except subprocess.CalledProcessError:
        print(f"Ping failed to {guest_ip}")


if __name__ == "__main__":
    testbed = load_testbed()
    menu()
