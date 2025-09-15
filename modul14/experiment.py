from genie.libs.conf.static_routing import StaticRouting
from pyats import topology

tb = topology.loader.load('../testbed2.yaml')
dev=tb.devices.CSR
sr = StaticRouting()
sr.devices = [dev]
sr.device_attr[dev].vrf_attr["default"].address_family_attr["ipv4"] \
  .route_attr["10.10.10.0/24"].next_hop_attr["192.0.2.1"]

cfg = sr.build_config(apply=False)
print(cfg.cli_config.data)