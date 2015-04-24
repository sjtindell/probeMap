import sqlite3

class Database(object):
	
	def __init__(self, filename):
		self.conn = sqlite3.connect(filename)
		self.cursor = self.conn.cursor()

	def __enter__(self):
		return self

	def __exit__(self, exctype, excinst, exctb):
		if exctype == Exception:
			# logging.exception('some text')
			pass
		else:
			self.conn.commit()
			self.conn.close()

	def create_mac_ssid_table(self):
		self.cursor.execute('''CREATE TABLE mac_to_ssid
				(mac, ssid)''')
		
	def insert_mac_ssid(self, mac, ssid):	
		self.cursor.execute('''INSERT INTO mac_to_ssid VALUES 
			({0}, {1})'''.format(mac, ssid))
