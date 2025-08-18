import json
import yaml

def get_device_info():
    device = {}
    device["type"] = input("Enter device type (switch/router): ")
    device["name"] = input("Enter device name: ")
    device["ports"] = int(input("Enter number of ports: "))
    device["ips"] = input("Enter IP addresses: ").split(",")
    device["speed"] = input("Enter port speed (1Gbps, 10Gbps): ")
    return device


if __name__ == "__main__":
    device_info = get_device_info()

    json_output = json.dumps(device_info, indent=4)
    print("\n--- JSON FORMAT ---")
    print(json_output)

    with open("device_info.yaml", "w") as yaml_file:
        yaml.dump(device_info, yaml_file, default_flow_style=False)

    print("\nYAML file 'device_info.yaml' has been created.")
