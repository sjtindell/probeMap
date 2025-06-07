#!/usr/bin/env python3

import sqlite3
from scapy.all import sniff, Dot11
from sqlwrap import Database

def check_packet(packet):
    if not packet.haslayer(Dot11):
        return

    # print full packet for debugging
    print(packet)

    if (packet.haslayer(Dot11) and
        packet.type == 0 and
        packet.subtype == 8 and
        packet.info and
        '\\x00' not in repr(packet.info) and
        '\\x82\\x04\\x0b\\x16\\x0c\\x12\\x18$' not in repr(packet.info)):
        
        print(f"Found SSID: {packet.info}")
        
        with Database('ssids.db') as db:
            if packet.info not in [str(ssid) for mac, ssid in db.ssids]:
                db.insert_mac_ssid(packet.addr2, packet.info)


def watch(interface):
    print(f"Starting capture on interface {interface}")
    sniff(iface=interface, prn=check_packet)


if __name__ == '__main__':
    watch('en0')

