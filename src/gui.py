#!/usr/bin/env python3

import os
import sys
import logging
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import Qt, QUrl
import gmap
import sniffer
from scraper import WigleQuery
from sqlwrap import Database

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def ensure_db():
	with Database('probemap.db') as db:
		db.create_mac_ssid_table()
		db.create_ssid_coords_table()
		db.create_ssid_map_table()

class MainWindow(QtWidgets.QWidget):

	def __init__(self, parent=None):
		super().__init__(parent)

		self.setWindowTitle('probeMap')
		self.setGeometry(1000, 800, 800, 800)

		self.layout = QtWidgets.QVBoxLayout(self)

		self.splitter = QtWidgets.QSplitter(Qt.Orientation.Vertical)
		self.layout.addWidget(self.splitter)

		self.top_widget = QtWidgets.QWidget()
		self.top_layout = QtWidgets.QVBoxLayout(self.top_widget)
		self.data_widget = QtWidgets.QListWidget()
		self.top_layout.addWidget(self.data_widget)
		self.splitter.addWidget(self.top_widget)

		self.map_widget = QWebEngineView()
		self.splitter.addWidget(self.map_widget)

		self.splitter.setSizes([300, 500])

		self.thread_pool = []

		self.packet_sniffer = sniffer.watch('en0')
		
		self.update_timer = QtCore.QTimer()
		self.update_timer.timeout.connect(self.update_list)
		self.update_timer.start(2000)  # Update every 2 seconds
		self.update_list()

		self.update_map()

	# on click	
	# start sniffing in bg
	
	# start query timer
	# if new ssid to be mapped: dont allow if query timer not 0
	# reset query timer to X on click
		
	def update_list(self):
		lister = ListWorker()
		lister.list_update.connect(self.update_list_widget)
		self.thread_pool.append(lister)
		lister.start()
	
	def update_list_widget(self, ssids):
		# Create a set of unique MAC/SSID pairs
		unique_pairs = set()
		for mac, ssid in ssids:
			unique_pairs.add((mac, ssid))
		
		self.data_widget.clear()
		for mac, ssid in sorted(unique_pairs):
			self.data_widget.addItem(f'{mac} -> {ssid}')

	def update_map(self):
		map_html = gmap.create_map()
		points_added = False
		with Database('probemap.db') as db:
			for mac, ssid in db.ssids:
				coords = db.get_ssid_coords(ssid)
				if not coords:
					token = os.getenv('WIGLE_API_TOKEN')
					if token:
						logger.info(f"Using auth token: {token[:10]}...")
					else:
						logger.warning("No Wigle API token found in environment!")
					query = WigleQuery(auth_token=token)
					response = query.query(ssid)
					logger.info(f"Got response for {ssid}: {len(response) if response else 0} results")
					list(query.store_results(ssid, response, db_path='probemap.db'))
					coords = db.get_ssid_coords(ssid)
				for lat, lon, country, region, city in coords:
					title = f"{ssid} ({city or ''}, {region or ''}, {country or ''})"
					map_html = gmap.add_point(map_html, float(lat), float(lon), title)
					points_added = True
					logger.info(f"Added point: {title} at ({lat}, {lon})")
		
		if points_added:
			# Use a fixed location in the project directory
			project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
			map_file = os.path.join(project_dir, "map.html")
			with open(map_file, 'w') as f:
				f.write(map_html)
			logger.info(f"Writing map to {map_file}")
			
			# Load the map in Qt
			url = QUrl.fromLocalFile(map_file)
			logger.info(f"Loading map from URL: {url.toString()}")
			self.map_widget.load(url)
			
			# Connect to loadFinished signal to verify map loaded
			self.map_widget.loadFinished.connect(self.on_map_loaded)
		else:
			logger.warning("No points to display on map")

	def on_map_loaded(self, success):
		if success:
			logger.info("Map loaded successfully in Qt")
		else:
			logger.error("Failed to load map in Qt")

	def new_map(self, ssid):
		token = os.getenv('WIGLE_API_TOKEN')
		query = WigleQuery(auth_token=token)
		response = query.query(ssid)
		with Database('probemap.db') as db:
			list(query.store_results(ssid, response, db_path='probemap.db'))
		self.update_map()

	def check_list_ssid(self, list_item):
		try:
			text = str(list_item.text())
			ssid_text = text.split()[2:]
			ssid = ' '.join(ssid_text)
			print(ssid)
		except AttributeError:
			ssid  = ''

		if ssid:
			with Database('probemap.db') as db:
				if ssid not in db.queried_ssids:
					self.new_map(ssid)

	def closeEvent(self, event):
		if hasattr(self, 'packet_sniffer'):
			self.packet_sniffer.stop()
		event.accept()


class SniffWorker(QtCore.QThread):

	def __init__(self, iface):
		super().__init__()
		self.iface = iface

	def __del__(self):
		self.wait()

	def run(self):
		sniffer.watch(self.iface)


class ListWorker(QtCore.QThread):

	list_update = QtCore.pyqtSignal(object)

	def __init__(self):
		super().__init__()

	def __del__(self):
		if self.isRunning():
			self.terminate()
			self.wait()

	def run(self):
		with Database('probemap.db') as db:
			self.list_update.emit(db.ssids)


if __name__ == '__main__':
	ensure_db()
	argv = sys.argv if len(sys.argv) > 0 else ["probeMap"]
	app = QtWidgets.QApplication(argv)
	window = MainWindow()
	window.show()
	sys.exit(app.exec())
