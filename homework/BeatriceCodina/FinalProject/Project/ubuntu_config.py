from lib.connectors.ssh_connection import SSHConnection
import re
import subprocess
import time

class UbuntuDevice:
    def __init__(self, ip, port=22, username="osboxes", password="osboxes.org"):
        self.conn = SSHConnection(ip=ip, port=port, username=username, password=password)

    def connect(self):
        return self.conn.connect()

    def execute(self, command):
        return self.conn.execute(command)

    def disconnect(self):
        self.conn.disconnect()

def get_interface_ip(iface):
    result = subprocess.run(
        ["ip", "-4", "addr", "show", iface],
        capture_output=True,
        text=True
    )
    match = re.search(r"inet (\d+\.\d+\.\d+\.\d+)/\d+", result.stdout)
    if match:
        return match.group(1)
    return None


def set_interface_ip(iface, ip, mask="24"):
    subprocess.run(["sudo", "ip", "addr", "flush", "dev", iface], check=True)
    subprocess.run(["sudo", "ip", "addr", "add", f"{ip}/{mask}", "dev", iface], check=True)
    subprocess.run(["sudo", "ip", "link", "set", iface, "up"], check=True)


if __name__ == "__main__":
    iface = "ens4"
    ip = get_interface_ip(iface)
    if ip:
        print(f"{iface} already has IP: {ip}")
    else:
        new_ip = "192.168.200.1"
        set_interface_ip(iface, new_ip)
        print(f"Set {new_ip}/24 on {iface}")

print('\x03')
