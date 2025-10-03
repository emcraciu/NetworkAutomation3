from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

try:
    import yaml
except ImportError as e:
    raise SystemExit("PyYAML is required. Install it with: pip install pyyaml") from e


def _ask(prompt: str, default: Optional[str] = None) -> str:
    while True:
        value = input(f"{prompt}{f' [{default}]' if default else ''}: ").strip()
        if value:
            return value
        if default is not None:
            return default
        print("Please enter a value.")


def _ask_int(prompt: str, default: Optional[int] = None, min_value: int = 0) -> int:
    while True:
        raw = input(f"{prompt}{f' [{default}]' if default is not None else ''}: ").strip()
        if not raw and default is not None:
            return default
        try:
            val = int(raw)
            if val < min_value:
                print(f"Value must be >= {min_value}.")
                continue
            return val
        except ValueError:
            print("Please enter a valid integer.")


def _ask_yes_no(prompt: str, default: bool = True) -> bool:
    default_str = "Y/n" if default else "y/N"
    while True:
        raw = input(f"{prompt} ({default_str}): ").strip().lower()
        if not raw:
            return default
        if raw in {"y", "yes"}:
            return True
        if raw in {"n", "no"}:
            return False
        print("Please answer y or n.")


def _ask_speed(prompt: str, default: str = "1G") -> str:
    common = ["10M", "100M", "1G", "2.5G", "5G", "10G", "25G", "40G", "100G", "200G", "400G"]
    choice = _ask(f"{prompt} (common: {', '.join(common)})", default)
    return choice.upper()


def get_device_info() -> Dict[str, Any]:
    device: Dict[str, Any] = {}
    device["type"] = _ask("Device type (switch/router)", "switch").lower()
    device["vendor"] = _ask("Vendor", "Cisco")
    device["model"] = _ask("Model", "Unknown")
    device["name"] = _ask("Hostname", "lab-device")
    device["location"] = _ask("Location", "LAB-RACK-1")

    device["mgmt"] = {
        "ip": _ask("Management IP (CIDR, e.g., 192.168.0.10/24)", "192.168.0.10/24"),
        "gateway": _ask("Default gateway (IP)", "192.168.0.1"),
        "vrf": _ask("Management VRF (or 'default')", "default"),
    }

    l3_count = _ask_int("How many L3 routed interfaces?", 1, min_value=0)
    l3_ifaces: List[Dict[str, Any]] = []
    for i in range(l3_count):
        print(f"\nL3 interface #{i + 1}")
        l3_ifaces.append(
            {
                "name": _ask("Interface name", f"GigabitEthernet0/{i}"),
                "description": _ask("Description", f"L3 link {i + 1}"),
                "ip": _ask("IP (CIDR, e.g., 10.0.0.1/30)", f"10.0.{i}.1/30"),
                "vrf": _ask("VRF (or 'default')", "default"),
                "enabled": _ask_yes_no("Enabled?", True),
            }
        )
    device["l3_interfaces"] = l3_ifaces

    port_count = _ask_int("How many ports (access/uplink/etc.)?", 4, min_value=0)
    ports: List[Dict[str, Any]] = []
    for p in range(port_count):
        print(f"\nPort #{p + 1}")
        port: Dict[str, Any] = {
            "name": _ask("Port name", f"GigabitEthernet1/0/{p}"),
            "description": _ask("Description", f"Port {p + 1}"),
            "speed": _ask_speed("Speed", "1G"),
            "enabled": _ask_yes_no("Admin up?", True),
        }
        # Simple L2/L3 role
        role = _ask("Role (access/trunk/l3)", "access").lower()
        port["role"] = role
        if role == "access":
            port["access_vlan"] = _ask_int("Access VLAN", 10, min_value=1)
        elif role == "trunk":
            port["native_vlan"] = _ask_int("Native VLAN", 1, min_value=1)
            port["allowed_vlans"] = _ask("Allowed VLANs (e.g., 10,20,30 or 10-20)", "1-4094")
        else:  # l3
            port["ip"] = _ask("IP (CIDR, e.g., 172.16.0.2/30)", f"172.16.{p}.2/30")
        ports.append(port)
    device["ports"] = ports

    if _ask_yes_no("Add tags?", False):
        tags_raw = _ask("Comma-separated tags", "lab,edge")
        device["tags"] = [t.strip() for t in tags_raw.split(",") if t.strip()]

    return device


def main() -> None:
    """
    Entry point:
      1) Collect device details from the user.
      2) Print JSON to stdout.
      3) Save YAML to 'device.yaml'.
    """
    device = get_device_info()

    print("\n=== JSON OUTPUT ===")
    print(json.dumps(device, indent=2))

    yaml_path = "device.yaml"
    with open(yaml_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(device, f, sort_keys=False)
    print(f"\nYAML saved to: {yaml_path}")


if __name__ == "__main__":
    main()
