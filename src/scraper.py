from urlparse import urlparse
import requests
from bs4 import BeautifulSoup
	

class WigleQuery(object):

	def __init__(self, ssid):
		self.ssid = ssid
	
	@property
	def response(self):
		wigle_api = 'https://wigle.net/gps/gps/main/confirmquery/?'
		cookie = 'auth=sjtindell%3A767294143%3A1413791126%3ANvAGsspBk%2B6SAsON%2FiRNiw'
		headers = {'Accept-Encoding': 'text/plain', 'Cookie': cookie}
		params = {'ssid': self.ssid}

		response = requests.get(wigle_api, params=params, headers=headers)
		html = BeautifulSoup(response.text)

		return html

	@property
	def coords(self):
		hrefs = [link.get('href') for link in self.response.find_all('a')]

		for link in hrefs:
			url = urlparse(link)
			q = str(url.query).strip()
			q = q.translate(None, 'maplt=onzoo')
			q = q.split('&')[0:2]
			if q != ['']:
				yield q[0], q[1]


