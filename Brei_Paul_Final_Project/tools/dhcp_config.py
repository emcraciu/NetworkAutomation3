dhcp_commands = [
    "\n",
    "conf t",
    "ip dhcp pool {name}",
    "network {network}",
    "default-router {gateway}",
    "dns-server {dns_server}",
    "domain-name {domain}",
    "exit",
    "ip dhcp excluded-address {excl_address}"
]