import sys
from PyQt4 import QtCore, QtGui, QtWebKit
import gmap

class MainWindow(QtGui.QWidget):

    def __init__(self, parent=None):

		QtGui.QWidget.__init__(self, parent)

		self.setWindowTitle('probeMap')
		self.setGeometry(1000, 800, 800, 800)

		self.layout = QtGui.QVBoxLayout(self)

		self.map_btn = QtGui.QPushButton('map ssid')
		self.connect(self.map_btn, QtCore.SIGNAL("released()"), self.run)

		self.data_widget = QtGui.QTextEdit()

		self.webview = QtWebKit.QWebView()
		self.webview.setHtml(gmap)

		self.layout.addWidget(self.map_btn)
		self.layout.addWidget(self.data_widget)
		self.layout.addWidget(self.webview)

		# threading
		# self.work_thread = None
		self.thread_pool = []

    def run(self):

        self.data_widget.clear()

        # connect to signal from different thread
        # self.work_thread = WorkThread()
        self.thread_pool.append(Worker())
        #self.connect(self.thread_pool[-1], 
			#QtCore.SIGNAL('update(QSTRING)', self.func)


class Worker(QtCore.QThread):
    def __init__(self):
        QtCore.QThread.__init__(self)

    def __del__(self):
        self.wait()

    def run(self):
        #for _ in range(500):
            #time.sleep(0.1)  # artificial time delay
            #self.emit(QtCore.SIGNAL('update(QString)'), "update")
		self.terminate()


if __name__ == '__main__':
    app = QtGui.QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
