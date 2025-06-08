#!/usr/bin/env python3

import os
from sqlwrap import Database


def create_map():
	return '''<!DOCTYPE html>
<html>
<head>
	<title>probeMap</title>
	<script>
		var mapInitialized = false;
		function initMap() {
			console.log("Initializing map...");
			window.map = new google.maps.Map(document.getElementById("map"), {
				zoom: 2,
				center: {lat: 0, lng: 0}
			});
			window.markers = [];
			window.bounds = new google.maps.LatLngBounds();
			window.mapReady = true;
			mapInitialized = true;
			console.log("Map initialized successfully");
		}

		// Check if map is ready every 100ms
		function checkMapReady() {
			if (!mapInitialized) {
				console.log("Map not initialized yet, waiting...");
				setTimeout(checkMapReady, 100);
			} else {
				console.log("Map is ready!");
			}
		}
		checkMapReady();
	</script>
	<script async defer
		src="https://maps.googleapis.com/maps/api/js?key=AIzaSyB41DRUbKWJHPxaFjMAwdrzWzbVKartNGg&callback=initMap">
	</script>
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
</body>
</html>'''


def add_point(map_html, lat, lng, title):
	script = '''
	<script>
		function addMarker() {
			console.log("Attempting to add marker...");
			if (window.mapReady && window.map && window.markers && window.bounds) {
				console.log("Adding marker:", %s, %s, "%s");
				var marker = new google.maps.Marker({
					position: {lat: %s, lng: %s},
					map: window.map,
					title: "%s"
				});
				window.markers.push(marker);
				window.bounds.extend(marker.getPosition());
				window.map.fitBounds(window.bounds);
				console.log("Marker added successfully");
			} else {
				console.log("Map not ready, retrying...");
				setTimeout(addMarker, 100);
			}
		}
		// Wait for map to be ready before adding marker
		if (mapInitialized) {
			addMarker();
		} else {
			console.log("Waiting for map to initialize before adding marker...");
			setTimeout(addMarker, 100);
		}
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
