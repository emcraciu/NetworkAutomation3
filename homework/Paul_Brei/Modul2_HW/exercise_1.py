result={}

def func():
    switch_dictionary={}
    while True:
        sw_name=input("Enter switch name or press q to exit: ")
        if sw_name=="q":
            break
        elif len(switch_dictionary)>0 and sw_name in switch_dictionary:
            print("A switch already exists with this name - no switch added! ")
            #continue
        else:
            if sw_name not in switch_dictionary:
                switch_dictionary[sw_name]={}
            while True:
                sw_port=input("Enter switch port or press q to exit: ")
                if sw_port == "q":
                    break
                elif sw_port in switch_dictionary[sw_name]:
                    print("This switch already has a port with this name - no port added! ")
                    #continue
                else:
                    switch_dictionary[sw_name][sw_port]=set()
                    while True:
                        vlans=input("Enter vlans or press q to exit: ")
                        vlan_set=set(vlans.split(","))
                        if "q" in vlans:
                            break
                        switch_dictionary[sw_name][sw_port].update(vlan_set)
                        print("current sw: ", switch_dictionary)

    return switch_dictionary

result=func()
print(result)
