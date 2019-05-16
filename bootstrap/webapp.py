#!/usr/bin/env python
# Copyright (c) 2015 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

from wsgiref import simple_server
from wsgiref.util import request_uri
import jsonrpclib
import re

TEMPLATE = """
hostname {}

aaa root nopassword
aaa authentication policy local allow-nopassword-remote-login
!
username admin privilege 15 role network-admin nopassword

interface Ethernet1
  no switchport
  ip address {}/31

ip routing

router ospf 65535
  max-lsa 12000
"""

def cli(commands):
    client = jsonrpclib.Server("unix:/var/run/command-api.sock")
    output = client.runCmds( 1, commands)
    return output

def get_ip_arp_port(remote_addr):
    """
    {
        "dynamicEntries": 1,
        "ipV4Neighbors": [
            {
                "hwAddress": "001c.738c.3ffb",
                "address": "169.254.0.5",
                "interface": "Ethernet3",
                "age": 0
            }
        ],
        "notLearnedEntries": 0,
        "totalEntries": 1,
        "staticEntries": 0
    }
    """
    response = cli(["show ip arp {}".format(remote_addr)])
    port = response[0]["ipV4Neighbors"][0]["interface"]
    return port

def get_lldp_neighbor_port(port):
    """
    {
        "tablesLastChangeTime": 1444689028.1416488,
        "tablesAgeOuts": 0,
        "tablesInserts": 16,
        "lldpNeighbors": [
            {
                "ttl": 120,
                "neighborDevice": "localhost",
                "neighborPort": "Ethernet1",
                "port": "Ethernet3"
            }
        ],
        "tablesDeletes": 15,
        "tablesDrops": 0
    }
    """
    response = cli(["show lldp neighbors {}".format(port)])
    port = response[0]["lldpNeighbors"][0]["neighborPort"]
    return port

def get_port_status(port):
    """
    {
        "interfaceStatuses": {
            "Ethernet3": {
                "vlanInformation": {
                    "interfaceMode": "routed",
                    "interfaceForwardingModel": "routed"
                },
                "bandwidth": 1000000000,
                "interfaceType": "1000BASE-T",
                "description": "vtep-03:ethernet1",
                "autoNegotiateActive": true,
                "duplex": "duplexFull",
                "autoNegotigateActive": true,
                "linkStatus": "connected",
                "lineProtocolStatus": "up"
            }
        }
    }
    """
    response = cli(["show interfaces {} status".format(port)])
    description = response[0]["interfaceStatuses"][port]["description"]
    status = response[0]["interfaceStatuses"][port]["lineProtocolStatus"]
    return status, description

def bootstrap(remote_addr):

    port = get_ip_arp_port(remote_addr)
    neighbor_port = get_lldp_neighbor_port(port)
    status, description = get_port_status(port)
    remote_host, neighbor_port_chk = description.split(":")

    # print "BOOTSTRAPPING:"
    # print "\tREMOTE_ADDR:", remote_addr
    # print "\tREMOTE_PORT:", neighbor_port, neighbor_port_chk
    # print "\tREMOTE_HOST:", remote_host
    # print "\tPORT:", port
    # print "\tSTATUS:", status
    # print "\tDESCRIPTION:", description

    return TEMPLATE.format(remote_host, remote_addr)

def application(environ, start_response):
    status = '200 OK'
    output = ""

    uri = request_uri(environ)
    remote_addr = environ["REMOTE_ADDR"]

    if re.search(r".*\/bootstrap\/?$", uri):
        output = bootstrap(remote_addr)

    response_headers = [('Content-type', 'text/plain'),
                        ('Content-Length', str(len(output)))]
    start_response(status, response_headers)

    return [output]

def main():
    httpd = simple_server.make_server('', 8080, application)
    httpd.serve_forever()

if __name__ == "__main__":
    main()
