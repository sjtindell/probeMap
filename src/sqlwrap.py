import sqlite3

class Database(object):
	
	def __init__(self, filename):
		self.conn = sqlite3.connect(filename)
		self.cursor = self.conn.cursor()

	# enter and exit methods allow use
	# of the pythonic "with" statement
	# and setup/teardown
	def __enter__(self):
		return self

	def __exit__(self, exctype, excinst, exctb):
		if exctype == Exception:
			# logging.exception('some text')
			pass
		else:
			self.conn.commit()
			self.conn.close()

	@property
	def ssids(self):
		self.cursor.execute('SELECT * FROM mac_to_ssid')
		return self.cursor.fetchall()

	@property
	def queried_ssids(self):
		self.cursor.execute('SELECT * FROM ssid_to_coords')
		return [location[0] for location in self.cursor.fetchall()]
		
	@property
	def mapped_ssids(self):
		self.cursor.execute('SELECT * FROM ssid_to_map')
		return [str(pair[0]) for pair in self.cursor.fetchall()]

		
	def create_mac_ssid_table(self):
		self.cursor.execute('''CREATE TABLE mac_to_ssid
				(mac, ssid)''')

	def create_ssid_coords_table(self):
		self.cursor.execute('''CREATE TABLE ssid_to_coords
			(ssid, lattitude, longitude)''')

	def create_ssid_map_table(self):
		self.cursor.execute('''CREATE TABLE ssid_to_map
			(ssid, html_string)''')
		
	def insert_mac_ssid(self, mac, ssid):
		cmd = 'INSERT INTO mac_to_ssid VALUES (?, ?)'	
		self.cursor.execute(cmd, (mac, ssid,))

	def insert_ssid_coords(self, ssid, lat, lon):
		cmd = 'INSERT INTO ssid_to_coords VALUES (?, ?, ?)'
		self.cursor.execute(cmd, (ssid, lat, lon,))

	def insert_ssid_map(self, ssid, html_string):
		cmd = 'INSERT INTO ssid_to_map VALUES (?, ?)'
		self.cursor.execute(cmd, (ssid, html_string,))
		
	def get_rows(self, table):
		string = 'SELECT * FROM {0}'
		cmd = string.format(table)
		self.cursor.execute(cmd)
		return self.cursor.fetchall()

	def get_ssid_coords(self, ssid):
		cmd = 'SELECT lattitude, longitude FROM ssid_to_coords WHERE ssid LIKE ?'
		self.cursor.execute(cmd, (ssid,))
		return self.cursor.fetchall()

	def get_ssid_map(self, ssid):
		cmd = 'SELECT html_string FROM ssid_to_map WHERE ssid=?'
		self.cursor.execute(cmd, (ssid,))
		html_string = self.cursor.fetchall()[0][0]
		return html_string

