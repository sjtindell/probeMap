#!/usr/bin/env python3

import os
import sys
import logging
import http.server
import socketserver
import threading
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage
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
		self.page = QWebEnginePage(self.map_widget)
		self.map_widget.setPage(self.page)
		self.splitter.addWidget(self.map_widget)

		self.splitter.setSizes([300, 500])

		self.thread_pool = []

		self.packet_sniffer = sniffer.watch('en0')
		
		self.update_timer = QtCore.QTimer()
		self.update_timer.timeout.connect(self.update_list)
		self.update_timer.start(2000)  # Update every 2 seconds
		self.update_list()

		# Start local server
		self.port = 8000
		self.server = None
		self.start_server()

		self.update_map()

	def start_server(self):
		class Handler(http.server.SimpleHTTPRequestHandler):
			def __init__(self, *args, **kwargs):
				super().__init__(*args, directory=os.path.dirname(os.path.dirname(os.path.abspath(__file__))), **kwargs)

		self.server = socketserver.TCPServer(("", self.port), Handler)
		self.server_thread = threading.Thread(target=self.server.serve_forever)
		self.server_thread.daemon = True
		self.server_thread.start()
		logger.info(f"Started local server on port {self.port}")

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
			map_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "map.html")
			with open(map_file, 'w') as f:
				f.write(map_html)
			logger.info(f"Writing map to {map_file}")
			
			# Load the map from the local server
			url = QUrl(f"http://localhost:{self.port}/map.html")
			logger.info(f"Loading URL: {url.toString()}")
			self.map_widget.load(url)
		else:
			logger.warning("No points to display on map")

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
		if self.server:
			self.server.shutdown()
			self.server.server_close()
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
