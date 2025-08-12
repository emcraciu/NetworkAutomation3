
def vlan_info():
    result = {}

    while True:
        sw_name = input("Enter the switch name ('q' to exit): ")
        if sw_name == 'q':
            break
        if sw_name not in result:
            result[sw_name] = {}
        else:
            continue

        while True:
            sw_port = input("Enter the switch port ('q' to exit): ")
            if sw_port == 'q':
                break
            if sw_port not in result[sw_name]:
                result[sw_name][sw_port] = {'vlans': []}
            else:
                continue
            vlans_set = set(result[sw_name][sw_port]['vlans'])
            vlans = set(input("Enter the vlans: ").split(","))
            for vlan in vlans:
                vlans_set.add(int(vlan))
                result[sw_name][sw_port]['vlans'] = sorted(vlans_set)

            while True:
                more_vlans = input("Enter more vlans for this port ('q' to exit): ")
                if more_vlans == 'q':
                    break
                more_vlans_set = set(more_vlans.split(","))
                for vlan in more_vlans_set:
                    vlans_set.add(int(vlan))
                result[sw_name][sw_port]['vlans'] = sorted(vlans_set)

    print(result)

vlan_info()









