def enter_sw_config():
    result = {} #the result dictionary

    while True:
        sw_name = input("Enter a switch name or q to quit: ")
        if sw_name.lower() == 'q': #as a convention we accept even Q
            break

        if sw_name not in result: #we check if the user provide same sw name
            result[sw_name] = {} #if not, we add the key
        #we can add an else branch for further information but for now we keep simple

        #port section now
        while True:
            sw_port = input(f"Enter a port for {sw_name} or q to quit the ports for {sw_name}: ")
            if sw_port.lower() == 'q':
                break

            if sw_port in result[sw_name]: #check if the user provide same port as before
                continue #if so, we wait skip the current iteration and ask for a new port

            vlan_set = set() #set of vlans so we dont have duplicates
            vlan_numbers = input(f"Enter VLAN numbers for {sw_port} as comma separated values (ex. 1,2,3): ")

            for vlan in vlan_numbers.split(','):
                vlan_set.add(int(vlan)) #we add as integers for further usage

            while True:
                more_vlans = input(f"Add more VLANs for {sw_port} as before (csv), or 'q' if no more: ")
                if more_vlans.lower() == 'q':
                    break

                for vlan in more_vlans.split(','):
                    vlan_set.add(int(vlan))

            result[sw_name][sw_port] = {'vlans': list(vlan_set)} # or sorted(vlan_set) -> direct a list from any iterable

    return result

vlan_data = enter_sw_config()
print(vlan_data)
