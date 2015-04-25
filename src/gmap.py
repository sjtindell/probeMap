import pygmaps
from scraper import WigleQuery
from sqlwrap import Database


def wigle_query(ssid):
	with Database('ssids.db') as db:
		response = WigleQuery(ssid)
		for lat, lon in response.coords:
			db.insert_ssid_coords(repr(ssid), lat, lon)


def draw_map(ssid, coords):
	gmap = pygmaps.maps('0', '0', '2')
	for location in coords:
		lat, lon = location
		gmap.addpoint(lat, lon, '#FF0000')
	gmap.draw('../ssid_html/{0}.html'.format(ssid.replace(' ', '_')))


def map_ssid_coords(ssid):
	with Database('ssids.db') as db:
		coords = db.get_ssid_coords(ssid)
		draw_map(ssid, coords)





