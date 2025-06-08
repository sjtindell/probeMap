#!/usr/bin/env python3

import os
import requests
import logging
from urllib.parse import quote
from sqlwrap import Database

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WigleQuery:
	def __init__(self, ssid=None, auth_token=None):
		self.ssid = ssid
		self.auth_token = auth_token or os.getenv('WIGLE_API_TOKEN')
		if not self.auth_token:
			logger.warning("No Wigle auth token provided. Set WIGLE_API_TOKEN environment variable or pass auth_token to constructor.")
		self.response = self.query() if self.ssid else None
	
	def query(self, ssid=None):
		ssid = ssid or self.ssid
		if not ssid:
			return None

		# Using the new API v2 endpoint for network search
		wigle_api = 'https://api.wigle.net/api/v2/network/search'
		headers = {
			'Authorization': f'Basic {self.auth_token}',
			'Accept': 'application/json'
		}
		params = {
			'ssid': ssid,
			'onlymine': 'false'
		}

		try:
			logger.info(f"Querying Wigle API v2 for SSID: {ssid}")
			response = requests.get(wigle_api, headers=headers, params=params)
			response.raise_for_status()
			data = response.json()
			logger.info(f"Got response from Wigle: {len(response.content)} bytes")
			results = data.get('results', [])
			logger.info(f"Found {len(results)} results in response")
			return results
		except requests.exceptions.RequestException as e:
			logger.error(f"Error querying Wigle API: {e}")
			return []

	def store_results(self, ssid=None, results=None, db_path='probemap.db'):
		"""Store the query results in the database."""
		ssid = ssid or self.ssid
		results = results if results is not None else self.response
		if not ssid or not results:
			return []
		logger.info(f"Found {len(results)} results in response")
		with Database(db_path) as db:
			for result in results:
				if 'trilat' in result and 'trilong' in result:
					lat = result['trilat']
					lon = result['trilong']
					country = result.get('country')
					region = result.get('region')
					city = result.get('city')
					logger.info(f"Storing coordinates: {lat}, {lon} ({city}, {region}, {country})")
					db.insert_ssid_coords(
						ssid, 
						str(lat), 
						str(lon),
						country,
						region,
						city
					)
					yield str(lat), str(lon)

	@property
	def coords(self):
		"""Get coordinates from the database for this SSID."""
		with Database('../ssids.db') as db:
			for lat, lon, country, region, city in db.get_ssid_coords(self.ssid):
				yield lat, lon



