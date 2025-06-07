#!/usr/bin/env python3

import os
import time
import sys

from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWebEngineWidgets import QWebEngineView

import gmap
import sniffer
from scraper import WigleQuery
from sqlwrap import Database


class MainWindow(QtWidgets.QWidget):

	def __init__(self, parent=None):
		super().__init__(parent)

		self.setWindowTitle('probeMap')
		self.setGeometry(1000, 800, 800, 800)

		self.layout = QtWidgets.QVBoxLayout(self)

		self.list_btn = QtWidgets.QPushButton('list ssids')
		self.list_btn.released.connect(self.update_list)

		self.data_widget = QtWidgets.QListWidget()
		self.data_widget.currentItemChanged.connect(self.check_list_ssid)
		self.webview = QWebEngineView()

		self.layout.addWidget(self.list_btn)
		self.layout.addWidget(self.data_widget)
		self.layout.addWidget(self.webview)

		self.thread_pool = []

		sniffer_worker = SniffWorker('en0')
		self.thread_pool.append(sniffer_worker)
		sniffer_worker.start()

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
		self.data_widget.clear()
		for mac, ssid in ssids:
			self.data_widget.addItem(f'{mac} -> {ssid}')

	def new_map(self, ssid):
		query = WigleQuery(ssid)
		# db open
		with Database('../ssids.db') as db:
			for lat, lon in query.coords:
				db.insert_ssid_coords(ssid, lat, lon)
		# db open
		gmap.map_ssid_coords(ssid)
		file_str = f'{os.path.abspath("../")}/ssid_html/{ssid.replace(" ", "_")}.html'
		with open(file_str, 'r') as f:
			html = f.read()
			# db open
			with Database('../ssids.db') as db:
				db.insert_ssid_map(ssid, html)
			self.webview.setHtml(html)

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
				if ssid in db.mapped_ssids:
					html = db.get_ssid_map(ssid)
					self.webview.setHtml(html)
					return
			self.new_map(ssid)
						


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
		self.wait()

	def run(self):
		with Database('../ssids.db') as db:
			self.list_update.emit(db.ssids)
		self.terminate()


if __name__ == '__main__':
	argv = sys.argv if len(sys.argv) > 0 else ["probeMap"]
	app = QtWidgets.QApplication(argv)
	window = MainWindow()
	window.show()
	sys.exit(app.exec())
