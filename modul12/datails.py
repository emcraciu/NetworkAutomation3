import ipaddress

intf = ipaddress.IPv4Interface('10.0.0.1/16')
print(intf.ip.compressed)
print(intf.ip.version)
print(intf.netmask)
print(intf.network.compressed)