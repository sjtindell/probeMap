import pygmaps
from sqlwrap import Database


def draw_map(ssid, coords):
	gmap = pygmaps.maps('0', '0', '2')
	for location in coords:
		lat, lon = location
		gmap.addpoint(float(lat), float(lon), '#FF0000')
	gmap.draw('../ssid_html/{0}.html'.format(ssid.replace(' ', '_')))


def map_ssid_coords(ssid):
	with Database('ssids.db') as db:
		coords = db.get_ssid_coords(ssid)
		draw_map(ssid, coords)

