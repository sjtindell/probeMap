from scapy.all import sniff, Dot11
import sqlite3

found_ssids = [ ]

def check_packet(pckt):
	if pckt.haslayer(Dot11) \
	and pckt.type == 0 \
	and pckt.subtype == 8 \
	and pckt.info != '' \
	and '\\x00' not in repr(pckt.info) \
	and pckt.addr2 not in found_ssids:
		found_ssids.append(pckt.addr2)
		db = sqlite3.connect('ssids.db')
		cursor = db.cursor()
		cursor.execute('''INSERT INTO mac_to_ssid VALUES 
			({0}, {1})'''.format(repr(pckt.addr2), repr(pckt.info)))
		db.commit()
		db.close()
	return

sniff(iface="mon0", prn=check_packet)
