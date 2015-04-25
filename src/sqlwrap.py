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
		

	def create_mac_ssid_table(self):
		self.cursor.execute('''CREATE TABLE mac_to_ssid
				(mac, ssid)''')

	def create_ssid_coords_table(self):
		self.cursor.execute('''CREATE TABLE ssid_to_coords
			(ssid, lattitude, longitude)''')
		
	def insert_mac_ssid(self, mac, ssid):	
		self.cursor.execute('''INSERT INTO mac_to_ssid VALUES 
			({0}, {1})'''.format(mac, ssid))

	def insert_ssid_coords(self, ssid, lat, lon):
		self.cursor.execute('''INSERT INTO ssid_to_coords VALUES 
			({0}, {1}, {2})'''.format(ssid, lat, lon))

	def get_rows(self, table, start=0, stop=0):
		string = 'SELECT * FROM {0} LIMIT {1}, {2}'
		cmd = string.format(table, start, stop if stop else start)
		self.cursor.execute(cmd)
		return self.cursor.fetchall()

	def get_ssid_coords(self, ssid):
		cmd = 'SELECT lattitude, longitude FROM ssid_to_coords WHERE ssid={0}'.format(repr(ssid))
		self.cursor.execute(cmd)
		return self.cursor.fetchall()

