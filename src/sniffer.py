#! /usr/env/python

import sqlite3
from scapy.all import sniff, Dot11
from sqlwrap import Database

def check_packet(pckt):
	if pckt.haslayer(Dot11) \
	and pckt.type == 0 \
	and pckt.subtype == 8 \
	and pckt.info != '' \
	and '\\x00' not in repr(pckt.info) \
	and '\\x82\\x04\\x0b\\x16\\x0c\\x12\\x18$' not in repr(pckt.info):
		with Database('ssids.db') as db:
			if pckt.info not in [str(ssid) for mac, ssid in db.ssids]:
				db.insert_mac_ssid(pckt.addr2, pckt.info)
	return

if __name__ == '__main__':
	sniff(iface="mon0", prn=check_packet)

