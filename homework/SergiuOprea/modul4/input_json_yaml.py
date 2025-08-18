#pentru routere pun porturi, dhcp_pool si usernames
#pentru switchuri pun porturi, vlanuri si default-gateway

import json
from unittest import case
import yaml
import re, sys


def add_device(equip, equip_dict):
    device = None
    while not device:
        device = re.match(r'[a-zA-Z][\w-]*', input(f"\n{equip} name(at least one letter) for creating: "))
    if device.string in equip_dict:
        print(f"{equip} already exists! Delete it first, then recreate it.")
        return
    print(f"Create new device {str(device.string)}")
    if equip == 'Router':
        equip_dict[device.string] = {'ports': {}, 'dhcp_pools': {}, 'usernames': []}
    elif equip == 'Switch':
        equip_dict[device.string] = {'ports': {}, 'vlans': [], 'default-gateways': []}


def delete_device(equip, equip_dict):
    device = None
    while not device:
        device = re.match(r'[a-zA-Z][\w-]*', input(f"\n{equip} name(at least one letter)for deleting: "))
    if device.string in equip_dict.keys():
        print(f"Deleting {device.string}...")
        del equip_dict[device.string]
        return
    print(f"{equip} doesn't exist.")


def edit_device(equip, equip_dict):
    device = None
    while not device:
        device = re.match(r'[a-zA-Z][\w-]*', input(f"\n{equip} name(at least one letter)for editing: "))
    if device.string in equip_dict:
        new = None
        while not new:
            new = re.match(r'[a-zA-Z][\w-]*', input(f"\n{equip} name(at least one letter) for rename: "))
        equip_dict[new.string] = equip_dict[device.string]
        del equip_dict[device.string]
        return
    print(f"{device.string} doesn't exist.")


def show_device(equip, equip_dict):
    device = None
    while not device:
        device = re.match(r'[a-zA-Z][\w-]*', input(f"\n{equip} name(at least one letter)for printing: "))
    if device.string in equip_dict:
        print(equip_dict[device.string])
        return
    print(equip_dict)
    print(f"{device.string} doesn't exist.")


def show_device_json(equip, equip_dict):
    device = None
    while not device:
        device = re.match(r'[a-zA-Z][\w-]*', input(f"\n{equip} name(at least one letter)for json printing: "))
    if device.string in equip_dict:
        print(json.dumps(equip_dict[device.string], indent=4))
        return
    print(f"{device.string} doesn't exist.")


def menu_storage(function_name: str, equip: str = None):
    menu_dict = {
        'main': """
    ===============================
                 MENU
    ===============================
    0.Exit
    1.Routers
    2.Switches
    """,
        'crud': f"""
    ===============================
                 MENU
    ===============================
    0.Exit
    1.Back
    2.Add {equip}
    3.Delete {equip}
    4.Edit {equip}
    5.Show {equip}
    6.Show json {equip}
    7.Show all
    8.Show all json
    9.Put {equip} devices in yaml file
    10.Configure {equip}
    """,
        'router_config': f"""
    0.Exit
    1.Back
    2.Add port
    3.Add dhcp_pool
    4.Add username
    5.Config port
    """,
        'switch_config': f"""
    0.Exit
    1.Back
    2.Add port
    3.Add vlan
    4.Add default-gateway
    5.Config port
    """,
        'config_router_port': f"""
    0.Exit
    1.Back
    2.Add ip
    3.Add speed
    """,
        'switch_port_config': f"""
    0.Exit
    1.Back
    2.Add vlan    
    """
    }
    return menu_dict[function_name]


def input_menu_validator(menu, options_cardinal):
    option = None
    while option not in range(options_cardinal):
        try:
            option = int(input("Choose a numbered option from menu: "))
        except Exception:
            print(menu)
            print("Only accepted input is a number from the menu. Try again.")
    return option


def router_config(router, equip_dict):
    menu = menu_storage(router_config.__name__)
    while True:
        print(menu)
        option = input_menu_validator(menu, 6)
        match option:
            case 0: sys.exit('Forced exit...')
            case 1:
                print("\nBack to previous menu...")
                break
            case 2: add_router_port(router, equip_dict)
            case 3: add_dhcp_pool(router, equip_dict)
            case 4: add_username(router, equip_dict)
            case 5:
                port = None
                while not port:
                    port = input("\nEnter router port: ")
                if port in equip_dict[router]['ports']:
                    config_router_port(router, port, equip_dict)
                else: print("Port {} doesn't exist.".format(port))


def add_router_port(router, equip_dict):
    port = None
    while not port:
        port = input(f"\n{router} port: ")
    if port in equip_dict[router]['ports']:
        print("\nPort already present.")
    else:
        equip_dict[router]['ports'][port] = {'ip': None, 'speed': None}


def add_dhcp_pool(router, equip_dict):
    pool = None
    while not pool:
        pool = input(f'\n{router} pool: "')
    if pool in equip_dict[router]['dhcp_pools']:
        print("\nPool already present.")
    else:
        equip_dict[router]['dhcp_pools'][pool] = {'gateway': None, 'address': None}

def add_username(router, equip_dict):
    username = None
    while not username:
        username = input(f"\n{router} username: ")
    if username in equip_dict[router]['usernames']:
        print("\nUsername already present.")
    else:
        equip_dict[router]['usernames'].append(username)


def config_router_port(router, port, equip_dict):
    menu = menu_storage(config_router_port.__name__)
    while True:
        print(menu)
        option = input_menu_validator(menu, 4)
        match option:
            case 0: sys.exit('Forced exit...')
            case 1:
                print("\nBack to previous menu...")
                break
            case 2: add_ip(router, port, equip_dict)
            case 3: add_router_port_speed(router, port, equip_dict)


def add_ip(router, port, equip_dict):
    ip = None
    while not ip:
        ip = input(f"\n{port} ip: ")
    if ip == equip_dict[router]['ports'][port]['ip']:
        print('IP already assigned')
    else:
        equip_dict[router]['ports'][port]['ip'] = ip


def add_router_port_speed(router, port, equip_dict):
    speed = None
    while not speed:
        speed = input(f"\n{port} speed: ")
    if speed == equip_dict[router]['ports'][port]['speed']:
        print("\nSpeed already present.")
    else:
        equip_dict[router]['ports'][port]['speed'] = speed


def switch_config(switch, equip_dict):
    menu = menu_storage(switch_config.__name__)
    while True:
        print(menu)
        option = input_menu_validator(menu, 6)
        match option:
            case 0: sys.exit('Forced exit...')
            case 1:
                print("\nBack to previous menu...")
                break
            case 2: add_switch_port(switch, equip_dict)
            case 3: add_vlan(switch, equip_dict)
            case 4: add_default_gateway(switch, equip_dict)
            case 5:
                port = None
                while not port:
                    port = input("\nEnter switch port: ")
                if port in equip_dict[switch]['ports']:
                    switch_port_config(switch, port, equip_dict)
                else: print("Port {} doesn't exist.".format(port))


def add_switch_port(switch, equip_dict):
    port = None
    while not port:
        port = input(f"\n{switch} port: ")
    if port in equip_dict[switch]['ports']:
        print("\nPort already present.")
    else:
        equip_dict[switch]['ports'][port] = {'vlan': None}


def add_vlan(switch, equip_dict):
    vlan = None
    while not vlan:
        vlan = input(f"\n{switch} vlan: ")
    if vlan in equip_dict[switch]['vlans']:
        print("\nVlan already present.")
    else:
        equip_dict[switch]['vlans'].append(vlan)


def add_default_gateway(switch, equip_dict):
    gateway = None
    while not gateway:
        gateway = input(f"\n{switch} gateway: ")
    if gateway in equip_dict[switch]['gateways']:
        print("\nGateway already present.")
    else:
        equip_dict[switch]['gateways'].append(gateway)


def switch_port_config(switch, port, equip_dict):
    menu = menu_storage(switch_port_config.__name__)
    while True:
        print(menu)
        option = input_menu_validator(menu, 3)
        match option:
            case 0:
                sys.exit('Forced exit...')
            case 1:
                print("\nBack to previous menu...")
                break
            case 2:
                add_port_vlan(switch, port, equip_dict)


def add_port_vlan(switch, port, equip_dict):
    vlan = None
    while not vlan:
        vlan = input(f"\n{switch} vlan: ")
    if vlan in equip_dict[switch]['vlans']:
        print("\nVlan already present.")
    else:
        equip_dict[switch]['ports'][port]['vlan'] = vlan


def crud(equip: str, equip_dict: {}):
    menu = menu_storage(crud.__name__, equip)
    while True:
        print(menu)
        option = input_menu_validator(menu, 11)
        match option:
            case 0: sys.exit('Forced exit...')
            case 1:
                print("\nBack to previous menu...")
                break
            case 2: add_device(equip, equip_dict)
            case 3: delete_device(equip, equip_dict)
            case 4: edit_device(equip, equip_dict)
            case 5: show_device(equip, equip_dict)
            case 6: show_device_json(equip, equip_dict)
            case 7: print(equip_dict)
            case 8: print(json.dumps(equip_dict, indent=4))
            case 9:
                with open(f'{equip}.yaml', 'w') as file:
                    file.write(yaml.dump(equip_dict))
                    print(f"{equip} yaml file written successfully.")
            case 10:
                device = None
                while not device:
                    device = re.match(r'[a-zA-Z][\w-]*', input(f"\n{equip} name(at least one letter) for configuring: "))
                if device.string in equip_dict:
                    if equip == 'Router':
                        router_config(device.string, equip_dict)
                    elif equip == 'Switch':
                        switch_config(device.string, equip_dict)
                else:
                    print(f"{device.string} doesn't exist.")

def main():
    switch_db = router_db = {}
    menu = menu_storage(main.__name__, None)
    while True:
        print(menu)
        option = input_menu_validator(menu, 3)
        match option:
            case 1: crud('Router', router_db)
            case 2: crud('Switch', switch_db)
            case 0:
                print("\nExiting...")
                break


if __name__ == "__main__":
    main()