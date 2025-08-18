'''
# functions and imports


1) Create function that will ask the user to provide information for a switch or router (name/ports/ips/speed/etc...)
2) import the module json and print the user provided information in json format
   - https://docs.python.org/3/library/json.html
3) import the module yaml and save the output yaml format
   - https://pyyaml.org/wiki/PyYAMLDocumentation
'''
import json
import yaml
def read_switch():
    name = input("Nume switch: ")
    ports = input("Numar porturi: ")
    speed = input("Viteza porturilor: ")
    adresa_ip= input("Adresa ip: ")
    return {
        "type": "switch",
        "name": name,
        "ports": ports,
        "speed": speed,
        "adresa_ip": adresa_ip
    }
def read_router():
    name = input("Nume router: ")
    ports = input("Numar porturi: ")
    interfaces = []
    n = int(input("Cate interfete au adresa IP?: "))
    for i in range(n):
        interface_name = input(f"Numele interfetei {i + 1}: ")
        interface_ip = input(f"Adresa IP pentru {interface_name}: ")
        interfaces.append({"name": interface_name, "ip": interface_ip})
    return {
        "type": "router",
        "name": name,
        "ports": ports,
        "interfaces": interfaces
    }
def print_in_json(data_to_print):
    print("\nDatele afisate in format JSON:")
    print(json.dumps(data, indent=4))
def save_in_yaml(all_data):
    with open("salvare_all.yaml", "w") as f:
        yaml.dump(all_data, f, sort_keys=False, default_flow_style=False)
    print("Datele au fost salvate in fisierul salvare_all.yaml")


all_data = []
while True:
    input_=input("Introdu numele echipamentului ales switch/router sau 'q' pentru a iesi: ")
    if input_.lower() == "q":
        print("Program terminat")
        break
    if input_.lower() == "switch":
        data=read_switch()
        all_data.append(data)
        print_in_json(data)
        save_in_yaml(all_data)
    elif input_.lower() == "router":
        data=read_router()
        all_data.append(data)
        print_in_json(data)
        save_in_yaml(all_data)
    else:
        print("Nu ati introdus un input valid, reincercati !")