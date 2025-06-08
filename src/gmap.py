#!/usr/bin/env python3

import os
from sqlwrap import Database


def create_map():
	return '''<!DOCTYPE html>
<html>
<head>
	<title>probeMap</title>
	<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
	<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
	<style>
		#map {
			height: 100%;
			width: 100%;
			position: absolute;
			top: 0;
			left: 0;
		}
		html, body {
			height: 100%;
			margin: 0;
			padding: 0;
		}
	</style>
</head>
<body>
	<div id="map"></div>
	<script>
		console.log("Initializing map...");
		var map = L.map('map').setView([0, 0], 2);
		L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
			attribution: '© OpenStreetMap contributors'
		}).addTo(map);
		window.markers = [];
		window.bounds = L.latLngBounds();
		console.log("Map initialized successfully");
	</script>
</body>
</html>'''


def add_point(map_html, lat, lng, title):
	script = '''
	<script>
		function addMarker() {
			if (window.map && window.markers && window.bounds) {
				console.log("Adding marker:", %s, %s, "%s");
				var marker = L.marker([%s, %s]).addTo(window.map);
				marker.bindPopup("%s");
				window.markers.push(marker);
				window.bounds.extend(marker.getLatLng());
				window.map.fitBounds(window.bounds);
				console.log("Marker added successfully");
			} else {
				console.log("Map not ready, retrying...");
				setTimeout(addMarker, 100);
			}
		}
		addMarker();
	</script>''' % (lat, lng, title, lat, lng, title)
	return map_html.replace('</body>', script + '\n</body>')


def map_ssid_coords(ssid):
	map_html = create_map()
	with Database('probemap.db') as db:
		for lat, lon in db.get_ssid_coords(ssid):
			map_html = add_point(map_html, float(lat), float(lon), ssid)
	
	file_str = f'{os.path.abspath("../")}/ssid_html/{ssid.replace(" ", "_")}.html'
	os.makedirs(os.path.dirname(file_str), exist_ok=True)
	with open(file_str, 'w') as f:
		f.write(map_html)
