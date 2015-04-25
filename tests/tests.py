import unittest
from db_api import Database
import sniffer


class SniffTest(unittest.TestCase):
	pass	


class DatabaseTest(unittest.TestCase):
	
	def setUp(self):
		self.db = Database('ssids.db')

	def tearDown(self):
		print('tear down!')

	def test_database_mac_to_ssid_rows_match_format(self):
		pass	
		
				


