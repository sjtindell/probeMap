#!/usr/bin/env python3

import sqlite3
import logging

logger = logging.getLogger(__name__)

class Database:
	
	def __init__(self, filename):
		self.conn = sqlite3.connect(filename)
		self.cursor = self.conn.cursor()
		self._init_tables()

	def _init_tables(self):
		"""Initialize all required tables if they don't exist."""
		self.create_mac_ssid_table()
		self.create_ssid_coords_table()
		self.create_ssid_map_table()
		self.conn.commit()

	# enter and exit methods allow use
	# of "with"
	def __enter__(self):
		return self

	def __exit__(self, exctype, excinst, exctb):
		if exctype == Exception:
			self.conn.rollback()
		else:
			self.conn.commit()
		self.conn.close()

	@property
	def ssids(self):
		"""Get all unique MAC/SSID pairs."""
		self.cursor.execute('SELECT DISTINCT mac, ssid FROM mac_to_ssid')
		return self.cursor.fetchall()

	@property
	def queried_ssids(self):
		"""Get all SSIDs that have been queried for coordinates."""
		self.cursor.execute('SELECT DISTINCT ssid FROM ssid_to_coords')
		return [location[0] for location in self.cursor.fetchall()]
		
	@property
	def mapped_ssids(self):
		"""Get all SSIDs that have been mapped."""
		self.cursor.execute('SELECT DISTINCT ssid FROM ssid_to_map')
		return [str(pair[0]) for pair in self.cursor.fetchall()]

		
	def create_mac_ssid_table(self):
		"""Create table for MAC to SSID mappings."""
		self.cursor.execute('''CREATE TABLE IF NOT EXISTS mac_to_ssid
				(mac TEXT, ssid TEXT, UNIQUE(mac, ssid))''')

	def create_ssid_coords_table(self):
		"""Create table for SSID to coordinates mappings."""
		self.cursor.execute('''CREATE TABLE IF NOT EXISTS ssid_to_coords
			(ssid TEXT, latitude TEXT, longitude TEXT, 
			 country TEXT, region TEXT, city TEXT,
			 UNIQUE(ssid, latitude, longitude))''')

	def create_ssid_map_table(self):
		"""Create table for SSID to map HTML mappings."""
		self.cursor.execute('''CREATE TABLE IF NOT EXISTS ssid_to_map
			(ssid TEXT PRIMARY KEY, html_string TEXT)''')
		
	def insert_mac_ssid(self, mac, ssid):
		"""Insert a MAC/SSID pair, ignoring duplicates."""
		try:
			cmd = 'INSERT OR IGNORE INTO mac_to_ssid VALUES (?, ?)'	
			self.cursor.execute(cmd, (mac, ssid))
		except sqlite3.Error as e:
			logger.error(f"Error inserting MAC/SSID pair: {e}")

	def insert_ssid_coords(self, ssid, lat, lon, country=None, region=None, city=None):
		"""Insert SSID coordinates with location info, ignoring duplicates."""
		try:
			cmd = '''INSERT OR IGNORE INTO ssid_to_coords 
					VALUES (?, ?, ?, ?, ?, ?)'''
			self.cursor.execute(cmd, (ssid, lat, lon, country, region, city))
		except sqlite3.Error as e:
			logger.error(f"Error inserting SSID coordinates: {e}")

	def insert_ssid_map(self, ssid, html_string):
		"""Insert or update SSID map HTML."""
		try:
			cmd = 'INSERT OR REPLACE INTO ssid_to_map VALUES (?, ?)'
			self.cursor.execute(cmd, (ssid, html_string))
		except sqlite3.Error as e:
			logger.error(f"Error inserting SSID map: {e}")
		
	def get_rows(self, table, limit=None):
		"""Get rows from a table with optional limit."""
		cmd = f'SELECT * FROM {table}'
		if limit:
			cmd += f' LIMIT {limit}'
		self.cursor.execute(cmd)
		return self.cursor.fetchall()

	def get_ssid_coords(self, ssid):
		"""Get all coordinates for a given SSID."""
		cmd = '''SELECT latitude, longitude, country, region, city 
				FROM ssid_to_coords WHERE ssid LIKE ?'''
		self.cursor.execute(cmd, (ssid,))
		return self.cursor.fetchall()

	def get_ssid_map(self, ssid):
		"""Get the map HTML for a given SSID."""
		cmd = 'SELECT html_string FROM ssid_to_map WHERE ssid=?'
		self.cursor.execute(cmd, (ssid,))
		result = self.cursor.fetchone()
		return result[0] if result else None

