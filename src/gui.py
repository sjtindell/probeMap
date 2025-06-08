#!/usr/bin/env python3

import os
import sys
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import Qt, QUrl
import gmap
import sniffer
from scraper import WigleQuery
from sqlwrap import Database

def ensure_db():
	with Database('../ssids.db') as db:
		db.create_mac_ssid_table()
		db.create_ssid_coords_table()
		db.create_ssid_map_table()

class MainWindow(QtWidgets.QWidget):

	def __init__(self, parent=None):
		super().__init__(parent)

		self.setWindowTitle('probeMap')
		self.setGeometry(1000, 800, 800, 800)

		# Create main layout
		self.layout = QtWidgets.QVBoxLayout(self)

		# Create splitter for resizable panes
		self.splitter = QtWidgets.QSplitter(Qt.Orientation.Vertical)
		self.layout.addWidget(self.splitter)

		# Top pane for SSID list
		self.top_widget = QtWidgets.QWidget()
		self.top_layout = QtWidgets.QVBoxLayout(self.top_widget)
		self.data_widget = QtWidgets.QListWidget()
		self.top_layout.addWidget(self.data_widget)
		self.splitter.addWidget(self.top_widget)

		# Bottom pane for map
		self.map_widget = QWebEngineView()
		self.splitter.addWidget(self.map_widget)

		# Set initial sizes
		self.splitter.setSizes([300, 500])

		self.thread_pool = []

		# Start packet capture
		self.packet_sniffer = sniffer.watch('en0')
		
		# Start periodic list updates
		self.update_timer = QtCore.QTimer()
		self.update_timer.timeout.connect(self.update_list)
		self.update_timer.start(2000)  # Update every 2 seconds
		self.update_list()

		# Create initial map
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
		# Create a new map
		map_html = gmap.create_map()
		
		# Add pins for all known locations
		with Database('../ssids.db') as db:
			for ssid in db.queried_ssids:
				coords = db.get_ssid_coords(ssid)
				for lat, lon in coords:
					gmap.add_point(map_html, float(lat), float(lon), ssid)
		
		# Save and display the map
		map_file = os.path.abspath("../map.html")
		with open(map_file, 'w') as f:
			f.write(map_html)
		self.map_widget.load(QUrl.fromLocalFile(map_file))

	def new_map(self, ssid):
		query = WigleQuery(ssid)
		with Database('../ssids.db') as db:
			for lat, lon in query.coords:
				db.insert_ssid_coords(ssid, lat, lon)
		self.update_map()  # Update map after adding new coordinates

	def check_list_ssid(self, list_item):
		try:
			text = str(list_item.text())
			ssid_text = text.split()[2:]
			ssid = ' '.join(ssid_text)
			print(ssid)
		# for when called by list btn click/change
		except AttributeError:
			ssid  = ''

		if ssid:
			with Database('../ssids.db') as db:
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
		with Database('../ssids.db') as db:
			self.list_update.emit(db.ssids)


if __name__ == '__main__':
	ensure_db()
	argv = sys.argv if len(sys.argv) > 0 else ["probeMap"]
	app = QtWidgets.QApplication(argv)
	window = MainWindow()
	window.show()
	sys.exit(app.exec())
