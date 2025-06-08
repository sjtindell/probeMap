#!/usr/bin/env python3

import sys
from sqlwrap import Database


def create_tables():
	with Database('probemap.db') as db:
		db.create_mac_ssid_table()
		db.create_ssid_coords_table()
		db.create_ssid_map_table()

def reset_tables():
	with Database('probemap.db') as db:
		cmds = (
			'DROP TABLE IF EXISTS mac_to_ssid',
			'DROP TABLE IF EXISTS ssid_to_coords',
			'DROP TABLE IF EXISTS ssid_to_map'
		)
		for cmd in cmds:
			db.cursor.execute(cmd)
	create_tables()

def see_table(table):
	with Database('probemap.db') as db:
		print(db.get_rows(table))

if __name__ == '__main__':
	arg = sys.argv[1] if len(sys.argv) > 1 else None
	if arg in ('--reset', 'reset'):
		reset_tables()
	elif arg in ('--see', 'see'):
		table = sys.argv[2] if len(sys.argv) > 2 else 'mac_to_ssid'
		see_table(table)
	else:
		create_tables()
