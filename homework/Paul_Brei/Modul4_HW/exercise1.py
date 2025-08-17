import json
import yaml

def get_switch_info():
    info={}
    n = int(input("Enter the number of entries: "))
    info = {input("Enter key: "): input("Enter value: ") for _ in range(n)}

    return info

def dict_to_json(dictionary):
    return json.dumps(dictionary)

def dict_to_yaml(dictionary):
    return yaml.dump(dictionary)

sw_info=get_switch_info()

json_string=dict_to_json(sw_info)
yaml_string=dict_to_yaml(sw_info)

print(f"json string:\n{json_string}")
print(80*'-')
print(f"yaml string:\n{yaml_string}")