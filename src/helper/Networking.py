# coding=utf-8
####################################################
# Helper methods for networks
#
# Author: Tobias Grupe
#
####################################################

import ipaddress


def is_valid_ip_address(ip_address):
    try:
        ipaddress.IPv4Address(ip_address)
        return True
    except ipaddress.AddressValueError:
        return False