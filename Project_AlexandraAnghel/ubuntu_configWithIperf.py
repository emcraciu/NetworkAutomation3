from lib.connectors.ssh_connection import SshConnection
import re
import subprocess
import time
import paramiko

class UbuntuDevice:
    def __init__(self, ip, port=22, username="osboxes", password="osboxes.org"):
        self.conn = SshConnection(host=ip, port=port, username=username, password=password)

    def connect(self):
        return self.conn.connect()

    def execute(self, command):
        return self.conn.exec_command(command)

    def disconnect(self):
        self.conn.disconnect()

def safe_execute(device, command, timeout=60):
    """
    Run a command on the remote host safely using exec_command.
    Use this for long-running or verbose commands (like apt-get).
    """
    stdin, stdout, stderr = device.conn.ssh.exec_command(command, timeout=timeout)
    out = stdout.read().decode()
    err = stderr.read().decode()
    return out + err

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


# ---------------------------
# Add static routes
# ---------------------------
def add_static_routes(server_ip, username="osboxes", password="osboxes.org"):
    device = UbuntuDevice(server_ip, username=username, password=password)
    device.connect()

    def sudo_cmd(cmd):
        return f"echo '{password}' | sudo -S {cmd}"

    print("[*] Adding static routes on Ubuntu server...")

    routes = [
        ("192.168.210.0/24", "192.168.200.10"),
        ("192.168.220.0/24", "192.168.200.20")
    ]

    for subnet, gw in routes:
        output = safe_execute(device, sudo_cmd(f"ip route add {subnet} via {gw} || true"))
        if output.strip():
            print(f"  Route add output: {output.strip()}")
        else:
            print(f"  Added route to {subnet} via {gw}")

    print("[*] Current routing table:")
    print(safe_execute(device, sudo_cmd("ip route show")))

    device.disconnect()

# ---------------------------
# IPERF SERVER LOGIC (as function)
# ---------------------------
def start_iperf_server(server_ip, username="osboxes", password="osboxes.org"):
    device = UbuntuDevice(server_ip, username=username, password=password)
    device.connect()

    # helper to prepend sudo with password
    def sudo_cmd(cmd):
        return f"echo '{password}' | sudo -S {cmd}"

    print("[*] Installing iperf3 if missing...")
    safe_execute(device, sudo_cmd("apt-get update -y && apt-get install -y iperf3"), timeout=180)

    print("[*] Killing old iperf3 instances...")
    safe_execute(device, sudo_cmd("pkill -f iperf3 || true"), timeout=10)

    print("[*] Starting iperf3 server on", server_ip)
    safe_execute(device, sudo_cmd("nohup iperf3 -s > /tmp/iperf_server.log 2>&1 &"), timeout=5)

    # quick check
    time.sleep(2)
    running = safe_execute(device, sudo_cmd("pgrep -a iperf3"), timeout=10)

    if "iperf3 -s" in running:
        print(f" iperf3 server is running successfully on {server_ip}:5201")
    else:
        print(f" Failed to start iperf3 server on {server_ip}")

    device.disconnect()


if __name__ == "__main__":
    iface = "ens4"
    ip = get_interface_ip(iface)
    if ip:
        print(f"{iface} already has IP: {ip}")
    else:
        new_ip = "192.168.200.1"
        set_interface_ip(iface, new_ip)
        print(f"Set {new_ip}/24 on {iface}")
        ip = new_ip

    add_static_routes(ip)
    start_iperf_server(ip)

print('\x03')