import NAME
import unittest


class Test(unittest.TestCase):
	
	def setup(self):
		print('setup!')

	def teardown(self):
		print('tear down!')

	def test_basic(self):
		print('i ran!')


if __name__ == '__main__':
	unittest.main()
