import json
import yaml


def collect_device_info():
    device_info = {}

    device_info['name'] = input("Device name: ").strip()

    try:
        port_count = int(input("Number of ports: "))
        device_info['ports'] = port_count
    except ValueError:
        device_info['ports'] = 0
        print("Invalid port count, set to 0")

    ips = []
    print("\nIP Address Configuration (press Enter with empty IP to finish):")
    while True:
        ip = input("IP address: ").strip()
        if not ip:
            break
        ips.append(ip)
    device_info['ips'] = ips

    device_info['mask'] = input("Subnet mask: ").strip()

    return device_info



device_data = collect_device_info()
print("JSON Format:")
print("-" * 20)
json_output = json.dumps(device_data, indent=2)
print(json_output)

print("\nYAML Format:")
print("-" * 20)
yaml_output = yaml.dump(device_data, default_flow_style=False, indent=2)
print(yaml_output)