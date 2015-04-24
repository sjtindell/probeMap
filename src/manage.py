import sqlite3
from db_api import Database

# for my initial testing, quickly build fresh db
if __name__ == '__main__':
	with Database('ssids.db') as db:
		db.create_mac_ssid_table()
	
