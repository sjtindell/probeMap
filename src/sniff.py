import sqlite3
from scapy.all import sniff, Dot11
from db_api import Database

found_ssids = [ ]

def check_packet(pckt):
	if pckt.haslayer(Dot11) \
	and pckt.type == 0 \
	and pckt.subtype == 8 \
	and pckt.info != '' \
	and '\\x00' not in repr(pckt.info) \
	and pckt.addr2 not in found_ssids:
		found_ssids.append(pckt.addr2)
		with Database('ssids.db') as db:
			db.insert_mac_ssid(repr(pckt.addr2), repr(pckt.info))
	return

sniff(iface="mon0", prn=check_packet)
