from ex1 import enter_device_config
import json

device_data = enter_device_config()
json_output = json.dumps(device_data, indent=4, sort_keys=True)
print(json_output)
