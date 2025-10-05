interface_commands = [
    "\n",
    "conf t",
    "int {interface}",
    'ip address {ip} {sm}',
    "no shutdown",
    "end",
]

ssh_commands = [
    "\n",
    "conf t",
    'hostname {hostname}',
    'ip domain name {domain}',
    'username {username} password {password}',
    'enable password {en_password}',
    'crypto key generate rsa modulus 2048',
    'line vty 0 4',
    'login local',
    'transport input ssh',
    'exit',
    'ip ssh version 2',
    'exit',

]