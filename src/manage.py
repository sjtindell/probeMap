import sqlite3
from sqlwrap import Database

# for my initial testing, quickly build fresh db
if __name__ == '__main__':
	with Database('ssids.db') as db:
		db.create_mac_ssid_table()
		db.create_ssid_coords_table()	
