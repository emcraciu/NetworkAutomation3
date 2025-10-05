bad_interface_commands = [
    "\n",
    "conf t",
    "int {interface}",
    'ip address {ip} {sm}',
    "no shutdown",
    "end",
]

bad_route_commands = [
    '\n',
    'conf t',
    "no ip route 192.168.250.0 255.255.255.0 192.168.240.5",
    "ip route 192.168.215.0 255.255.255.0 192.168.230.3",
    "ip route 192.168.220.0 255.255.255.0 192.168.200.3",
    "exit"
]