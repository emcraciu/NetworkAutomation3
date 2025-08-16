from ex1 import enter_device_config
from yaml import dump

yaml_output = dump(
    enter_device_config(),
    default_flow_style=False
)
print("\nYAML output:\n", yaml_output)
