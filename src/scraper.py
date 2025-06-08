#!/usr/bin/env python3

from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WigleQuery:

	def __init__(self, ssid, auth_token=None):
		self.ssid = ssid
		self.auth_token = auth_token or os.getenv('WIGLE_AUTH_TOKEN')
		if not self.auth_token:
			logger.warning("No Wigle auth token provided. Set WIGLE_AUTH_TOKEN environment variable or pass auth_token to constructor.")
	
	@property
	def response(self):
		wigle_api = 'https://wigle.net/gps/gps/main/confirmquery/?'
		headers = {
			'Accept-Encoding': 'text/plain',
			'Authorization': f'Basic {self.auth_token}',
			'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
		}
		params = {'ssid': self.ssid}

		try:
			logger.info(f"Querying Wigle for SSID: {self.ssid}")
			response = requests.get(wigle_api, params=params, headers=headers)
			response.raise_for_status()
			html = BeautifulSoup(response.text, 'html.parser')
			logger.info(f"Got response from Wigle: {len(response.text)} bytes")
			return html
		except requests.exceptions.RequestException as e:
			logger.error(f"Error querying Wigle: {e}")
			return None

	@property
	def coords(self):
		if not self.response:
			return []
			
		hrefs = [link.get('href') for link in self.response.find_all('a')]
		logger.info(f"Found {len(hrefs)} links in response")

		for link in hrefs:
			url = urlparse(link)
			q = str(url.query).strip()
			q = q.translate(str.maketrans('', '', 'maplt=onzoo'))
			q = q.split('&')[0:2]
			if q != ['']:
				logger.info(f"Found coordinates: {q[0]}, {q[1]}")
				yield q[0], q[1]



