# check if second interface has IP and if not set IP
# Silviu
import re
import subprocess
import time

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

# Sergiu
# sa setam adresa ip pe a 2a interfata si prima data sa verificam ca nu avem adresa ip



result = subprocess.run(['ip', 'addr'],
                        stdin=subprocess.PIPE,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        check=True
                        )
# print(result.stdout)
have_ip = re.compile(r'inet.*ens4')
ip_done = None
try:
    response = re.search(have_ip, result.stdout)
    print(response.group(0))
except Exception as e:
    print('ens4 does not have an ip add\nadding one...')
    sudo_job = subprocess.Popen(['sudo', 'su'],
                                stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                text=True,
                                shell=True
                                )
    time.sleep(1)
    std_out, std_err = sudo_job.communicate("osboxes.org")
    print(std_out)
    ip_done = subprocess.run(['sudo', 'ip', 'addr', 'add', '192.168.200.66/24', 'dev', 'ens4'],
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             text=True
                             )
    print(ip_done.stdout)

result = subprocess.run(['ip', 'addr'],
                        stdin=subprocess.PIPE,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        )
try:
    rezzy = re.search(have_ip, result.stdout).group(0).split()[1].split('/')[0]
    print(rezzy)
except Exception as e:
    print('ip was tried to be given, though somehow failed' + str(e))
