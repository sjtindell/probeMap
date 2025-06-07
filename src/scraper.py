#!/usr/bin/env python3

from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
	

class WigleQuery:

	def __init__(self, ssid):
		self.ssid = ssid
	
	@property
	def response(self):
		wigle_api = 'https://wigle.net/gps/gps/main/confirmquery/?'
		cookie = ''
		headers = {'Accept-Encoding': 'text/plain', 'Cookie': cookie}
		params = {'ssid': self.ssid}

		response = requests.get(wigle_api, params=params, headers=headers)
		html = BeautifulSoup(response.text, 'html.parser')

		return html

	@property
	def coords(self):
		hrefs = [link.get('href') for link in self.response.find_all('a')]

		for link in hrefs:
			url = urlparse(link)
			q = str(url.query).strip()
			q = q.translate(str.maketrans('', '', 'maplt=onzoo'))
			q = q.split('&')[0:2]
			if q != ['']:
				yield q[0], q[1]



