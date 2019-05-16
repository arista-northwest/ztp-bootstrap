#!/usr/bin/env python
from __future__ import unicode_literals
import ipaddress

FIRST_NETWORK = u"169.254.0.0/31"

interfaces = range(1, 33)

dhcpd_template = """subnet {0} netmask 255.255.255.254 {{
  option routers {0};
  pool {{
        range {1} {1};
        allow members of "ARISTA";
  }}
}}"""

intf_template = """interface Ethernet{0}
  no switchport
  description tor-{0:02d}:ethernet1
  ip address {1}/31"""

dhcp_config = []
intf_config = []
last_network = None
for intf in interfaces:
    if not last_network:
        network = ipaddress.ip_network(FIRST_NETWORK)
    else:
        network = ipaddress.ip_network("{}/31".format(last_network[-1] + 1))
        #network = ipaddress.ip_network()

    dhcp_config.append(dhcpd_template.format(str(network[0]), str(network[1])))
    intf_config.append(intf_template.format(intf, network[0]))
    last_network = network

print "\n\n".join(dhcp_config)

print "\n!\n".join(intf_config)
