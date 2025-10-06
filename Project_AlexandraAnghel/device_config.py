def set_device_hostname(device):
    target_hostname = f"{device.name}1"
    device.configure(f"hostname {target_hostname}")
    return True

def get_device_prompt(device):
    return f"{device.name}#"