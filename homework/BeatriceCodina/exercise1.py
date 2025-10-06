import pprint

def vlan_information():
    result = {}
    while True:
        switch_name = input("Enter switch name or 'q' to quit: ")
        if switch_name == "q":
            break
        if switch_name in result:
            print(f"Switch {switch_name} already exists, please enter another name")
            continue
        else:
            result[switch_name] = {}

            while True:
                switch_port = input("Enter switch port or 'q' to quit:")
                if switch_port == "q":
                    break
                if switch_port in result[switch_name]:
                    print(f"Switch {switch_port} already exists, please enter another port")
                    continue
                else:
                    vlans = set()

                while True:
                    vlan_input = input(f"Enter VLANs corresponding to switch port {switch_port} or 'q' to quit:")
                    if vlan_input == "q":
                        break
                    for vlan in vlan_input.split(","):
                        vlan_number = int(vlan)
                        vlans.add(vlan_number)

                print(f"Vlans for this port: {vlans}")

                result[switch_name][switch_port] = {"vlans": vlans}

    return result

pprint.pprint(vlan_information(), indent = 2)

