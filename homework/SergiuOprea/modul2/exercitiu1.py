# Exercise 1 - read module3 first
# Create and call python function that will collect vlan information for each port of a switch and return a dictionary as in the example below:
#
# result = {
#     'SW1': {
#         'Ethernet1/1': {'vlans': [100, 200, 300]},
#         'Ethernet1/2': {'vlans': [100, 500, 20]},
#     },
#     'SW2': {
#         'Ethernet1/1': {'vlans': [10, 20, 30]},
#         'Ethernet1/4': {'vlans': [11, 12, 13]},
#     }
# }
# Steps:
# ask user for switch name
# ask user for switch port
# ask user for vlans corresponding to above port
# user will provide vlans as "100,200,300"
# user will be asked to add more vlans or press q
# if no more vlans are provided user will be asked to provide additional port or press 'q'
# if no more ports are provided user will be asked ro provide additional switch or press 'q'
# Checks:
# make sure that vlans do not repeat for port - hint: set()
# check if user provides same port name a second time
# check if user provides same switch name a second time

from pprint import pprint

def switch_name_validator(switch_name):
    if switch_name[:-1] != "SW" or int(switch_name[-1]) < 0 or int(switch_name[-1]) > 9:
        print("Only name form allowed is 'SWx' with x an integer in [0,9].\nTry again.")
        return False
    if switch_name in switch_db:
        choice = None
        while choice not in ['a','do']:
            choice = input('Switch exists. Type "do" to delete and overwrite it. Type "a" to introduce another.\n:')
        if choice == "do":
            switch_db.pop(switch_name)
            return True
        if choice == 'a':
            return False
    return True

def switch_port_validator(switch_port, switch_name):
    if switch_port[:-1] != "Ethernet1/" or int(switch_port[-1]) < 1 or int(switch_port[-1]) > 9:
        print("Allowed name form is 'Ethernet1/x' with x an integer in [0,9].\nTry again.")
        return False
    if switch_port in switch_db[switch_name]:
        choice = None
        while choice not in ['a','do']:
            choice = input('Port exists. Type "do" to delete and overwrite it. Type "a" to introduce another.\n:')
        if choice == "do":
            switch_db[switch_name].pop(switch_port)
            return True
        if choice == 'a':
            return False
    return True

def switch_vlan_validator(switch_vlan_string):
    if switch_vlan_string == (vlan_list := switch_vlan_string.split(',')):
        print("There was not even a ',' provided. Try again respecting the formula.")
        return False
    for vlan in vlan_list:
        if int(vlan) < 2 or int(vlan) > 4096:
            print("VLANs are only in [2,4096] range.")
            return False
    return True

def vlan_loop(switch_name, switch_port):
    while True:
        switch_vlan_string = input("Give switch vlans string of the form: '100,200,300' or press 'q' to"
                                   "quit. Duplicate vlans will be automatically not added.\n: ")
        match switch_vlan_string:
            case 'q':
                break
            case _:
                if not switch_vlan_validator(switch_vlan_string):
                    continue
                int_vlan_list = []
                vlan_list = switch_vlan_string.split(',')
                for vlan in vlan_list:
                    int_vlan_list.append(int(vlan))
                switch_db[switch_name][switch_port].extend(int_vlan_list)
                switch_db[switch_name][switch_port] = list(set(switch_db[switch_name][switch_port]))

def port_loop(switch_name):
    while True:
        switch_port = input("Give switch port like 'Ethernet1/x' with x in [1,9] or press q to quit: ")
        match switch_port:
            case 'q':
                break
            case _:
                if not switch_port_validator(switch_port, switch_name):
                    continue
                switch_db[switch_name].update({f'{switch_port}': []})
                vlan_loop(switch_name, switch_port)

switch_db = {}

def main():
    while True:
        switch_name = input("Give switch name or press 'q' to quit. Name must be 'SWx' with x an integer in [0,9].\n:")
        match switch_name:
            case "q":
                break
            case _:
                if not switch_name_validator(switch_name):
                    continue
                switch_db[switch_name] = {}
                port_loop(switch_name)

if __name__ == '__main__':
    main()
    pprint(switch_db, indent=4, width=50)


