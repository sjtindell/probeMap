import pygmaps
import webbrowser
from scraper import WigleQuery
from sqlwrap import Database


ssid = 'Ocean Gate Wifi'

def ssid_query(ssid):
	with Database('ssids.db') as db:
		response = WigleQuery(ssid)
		for lat, lon in response.coords:
			db.insert_ssid_coords(repr(ssid), lat, lon)


def open_map(coords):
	gmap = pygmaps.maps('0', '0', '2')
	for location in coords:
		lat, lon = location
		gmap.addpoint(lat, lon, '#FF0000')
	url = './ssid_map.html'
	gmap.draw(url)
	webbrowser.open_new_tab(url)


def map_ssid_coords(ssid):
	with Database('ssids.db' as db:
		coords = db.get_ssid_coords(ssid)
		open_map(coords)




