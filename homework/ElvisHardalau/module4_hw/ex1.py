import json


def enter_device_config():
    result = {} #the result dictionary

    device_name = input("Enter a switch or a router name: ")

    if device_name not in result: #we check if the user provide same sw name
        result[device_name] = {} #if not, we add the key
    #we can add an else branch for further information but for now we keep simple


    #port section now
    while True:
        device_port = input(f"Enter a port for {device_name} or q to quit the ports for {device_name}: ")
        if device_port.lower() == 'q':
           break

        if device_port in result[device_name]: #check if the user provide same port as before
            continue #if so, we wait skip the current iteration and ask for a new port

        result[device_name][device_port] = {}
        device_port_speed = input(f"Enter speed for port {device_port} of {device_name}: ")
        result[device_name][device_port]['speed'] = device_port_speed

        device_port_ip = input(f"Enter a ip for port {device_port} of {device_name} ")
        result[device_name][device_port]['ip'] = device_port_ip

        vlan_set = set() #set of vlans so we dont have duplicates
        vlan_numbers = input(f"Enter VLAN numbers for {device_port} as comma separated values (ex. 1,2,3): ")

        for vlan in vlan_numbers.split(','):
            vlan_set.add(int(vlan)) #we add as integers for further usage

        while True:
            more_vlans = input(f"Add more VLANs for {device_port} as before (csv), or 'q' if no more: ")
            if more_vlans.lower() == 'q':
                break

            for vlan in more_vlans.split(','):
                vlan_set.add(int(vlan))

        result[device_name][device_port]['vlans'] = list(vlan_set) # or sorted(vlan_set) -> direct a list from any iterable

    return result

if __name__ == '__main__':
    device_data = enter_device_config()
    print(device_data)
