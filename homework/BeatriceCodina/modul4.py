import json
import yaml

def enter_string(what):
    return input(f"Please enter {what}: ")

def enter_int(what):
    return int(input(f"Please enter {what}: "))

def create_device():
    device = {}
    device["type"] = enter_string("device type (switch or router)")
    device["name"] = enter_string("device name")
    device["ports"] = enter_int("number of ports")
    device["ip"] = enter_string("IP address")
    device["speed"] = enter_string("port speed")

    print("\nDevice info in JSON format:\n")
    print(json.dumps(device, indent=4))

    with open("device.yaml", "w") as file:
        yaml.dump(device, file)

create_device()
