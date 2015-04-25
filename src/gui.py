import os
import time
import sys
from PyQt4 import QtCore, QtGui, QtWebKit
import gmap
from sqlwrap import Database


class MainWindow(QtGui.QWidget):

	def __init__(self, parent=None):

		QtGui.QWidget.__init__(self, parent)

		self.setWindowTitle('probeMap')
		self.setGeometry(1000, 800, 800, 800)

		self.layout = QtGui.QVBoxLayout(self)

		self.list_btn = QtGui.QPushButton('list ssids')
		self.connect(self.list_btn, QtCore.SIGNAL("released()"), self.run_list)

		self.data_widget = QtGui.QListWidget()
		self.data_widget.currentItemChanged.connect(self.display_google_map)
		self.webview = QtWebKit.QWebView()

		self.layout.addWidget(self.list_btn)
		self.layout.addWidget(self.data_widget)
		self.layout.addWidget(self.webview)

		self.thread_pool = []
	
	# start sniffing in bg
	
	# start query timer
	# reset query timer on list_click
	
	
	def update_ssid_list(self, ssids):
		self.data_widget.clear()
		for mac, ssid in ssids:
			self.data_widget.addItem('{0} -> {1}'.format(mac, ssid))

	def display_google_map(self, list_item_txt):
		ssid = ' '.join(str(list_item_txt.text()).split()[2:])
		with Database('ssids.db') as db:
			if ssid in db.queried_ssids:
				gmap.map_ssid_coords(ssid)
			else:
				gmap.wigle_query(ssid)
				gmap.map_ssid_coords(ssid)
		file_str = '{0}/ssid_html/{1}.html'.format(os.path.abspath('../'), ssid.replace(' ', '_'))
		with open(file_str, 'r') as f:
			self.webview.setHtml(f.read())

	def run_list(self):
		lister = ListWorker()
		lister.list_update.connect(self.update_ssid_list)
		self.thread_pool.append(lister)
		lister.start()

		


class ListWorker(QtCore.QThread):

	list_update = QtCore.pyqtSignal(object)

	def __init__(self):
		QtCore.QThread.__init__(self)

	def __del__(self):
		self.wait()

	def run(self):
		while True:
			time.sleep(1)
			with Database('ssids.db') as db:
				self.list_update.emit(db.ssids)
			self.terminate()


if __name__ == '__main__':
	app = QtGui.QApplication([])
	window = MainWindow()
	window.show()
	sys.exit(app.exec_())
