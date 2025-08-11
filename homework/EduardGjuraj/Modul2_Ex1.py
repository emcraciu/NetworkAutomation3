"""
Create and call python function that will collect vlan information for each port of a switch and return a dictionary as in the example below:

result = {
    'SW1': {
        'Ethernet1/1': {'vlans': [100, 200, 300]},
        'Ethernet1/2': {'vlans': [100, 500, 20]},
    },
    'SW2': {
        'Ethernet1/1': {'vlans': [10, 20, 30]},
        'Ethernet1/4': {'vlans': [11, 12, 13]},
    }
}
Steps:
ask user for switch name
ask user for switch port
ask user for vlans corresponding to above port
user will provide vlans as "100,200,300"
user will be asked to add more vlans or press q
if no more vlans are provided user will be asked to provide additional port or press 'q'
if no more ports are provided user will be asked ro provide additional switch or press 'q'
Checks:
make sure that vlans do not repeat for port - hint: set()
check if user provides same port name a second time
check if user provides same switch name a second time
"""
import json

result = {}
while True:
    switch_name=input("Enter switch name (or press 'q' to exit): ")
    if switch_name == 'q':
        break
    if switch_name in result:
        print("Switch name already used.")
        continue

    result[switch_name] = {}
    while True:
        port_name=input(f"Enter switch port for {switch_name} (or press 'q' to exit): ")
        if port_name == 'q':
            break
        if port_name in result[switch_name]:
            print("Port already used in this switch")
            continue
        vlans = set()

        while True:
            vlan_name=input(f"Enter VLAN for {switch_name}/{port_name} (or press 'q' to exit): ")
            if vlan_name == 'q':
                break
            new_vlans = []
            for v in vlan_name.split(','):
                new_vlans.append(int(v.strip()))
            vlans.update(new_vlans)
            result[switch_name][port_name] = {'vlans': sorted(list(vlans))}

print(json.dumps(result, indent=2))

