import sys
import sqlite3
from sqlwrap import Database

# for my initial testing, quickly build fresh db
if __name__ == '__main__':
	arg = None
	
	try:
		arg = sys.argv[1]
	except IndexError:
		pass

	if arg == 'del':
		table = sys.argv[2]
		with Database('ssids.db') as db:
				if table == 'all':
					cmds = (
						'DELETE FROM mac_to_ssid',
						'DELETE FROM ssid_to_coords',
						'DELETE FROM ssid_to_map'
					)
					for cmd in cmds:
						db.cursor.execute(cmd)
				else:
					db.cursor.execute('DELETE FROM {0}'.format(table))
	elif arg == 'see':
		table = sys.argv[2]
		with Database('ssids.db') as db:
			print db.get_rows('mac_to_ssid', 10)
	else:
		with Database('ssids.db') as db:
			db.create_mac_ssid_table()
			db.create_ssid_coords_table()
			db.create_ssid_map_table()
