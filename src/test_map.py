#!/usr/bin/env python3

import sys
import os
import http.server
import socketserver
import threading
from PyQt6 import QtWidgets, QtCore
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage
from PyQt6.QtCore import QUrl, QTimer

def create_simple_map():
    return '''<!DOCTYPE html>
<html>
<head>
    <title>Simple Map Test</title>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
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
    <script>
        console.log("Initializing map...");
        var map = L.map('map').setView([37.7749, -122.4194], 13);  // San Francisco
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors'
        }).addTo(map);

        // Add a marker
        var marker = L.marker([37.7749, -122.4194]).addTo(map);
        marker.bindPopup("<b>San Francisco</b><br>Test marker").openPopup();
        
        console.log("Map initialized successfully with marker");
    </script>
</body>
</html>'''

class TestWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Map Test')
        self.setGeometry(100, 100, 800, 600)

        # Create layout
        layout = QtWidgets.QVBoxLayout(self)
        
        # Create web view with custom page
        self.web_view = QWebEngineView()
        self.page = QWebEnginePage(self.web_view)
        self.web_view.setPage(self.page)
        layout.addWidget(self.web_view)

        # Create and write map file
        map_html = create_simple_map()
        map_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "test_map.html")
        with open(map_file, 'w') as f:
            f.write(map_html)
        print(f"Wrote map to: {map_file}")

        # Start a local server
        self.port = 8000
        self.server = None
        self.start_server()

        # Load the map from the local server
        url = QUrl(f"http://localhost:{self.port}/test_map.html")
        print(f"Loading URL: {url.toString()}")
        
        # Connect signals
        self.web_view.loadFinished.connect(self.on_load_finished)
        self.page.loadFinished.connect(self.on_page_load_finished)
        
        # Set up a timer to check if the map is visible
        self.check_timer = QTimer()
        self.check_timer.timeout.connect(self.check_map_visibility)
        self.check_timer.start(1000)  # Check every second
        
        # Load the URL
        self.web_view.load(url)

    def start_server(self):
        class Handler(http.server.SimpleHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory=os.path.dirname(os.path.dirname(os.path.abspath(__file__))), **kwargs)

        self.server = socketserver.TCPServer(("", self.port), Handler)
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.daemon = True
        self.server_thread.start()
        print(f"Started local server on port {self.port}")

    def on_load_finished(self, success):
        if success:
            print("WebView load finished successfully!")
        else:
            print("WebView failed to load!")

    def on_page_load_finished(self, success):
        if success:
            print("Page load finished successfully!")
            # Try to inject some JavaScript to check if the map is there
            self.web_view.page().runJavaScript("""
                if (typeof L !== 'undefined') {
                    console.log('Leaflet is loaded');
                } else {
                    console.log('Leaflet is not loaded');
                }
            """)
        else:
            print("Page failed to load!")

    def check_map_visibility(self):
        # Check if the map div is visible
        self.web_view.page().runJavaScript("""
            var mapDiv = document.getElementById('map');
            if (mapDiv) {
                console.log('Map div exists, dimensions:', 
                    mapDiv.offsetWidth, 'x', mapDiv.offsetHeight);
            } else {
                console.log('Map div not found');
            }
        """)

    def closeEvent(self, event):
        if self.server:
            self.server.shutdown()
            self.server.server_close()
        super().closeEvent(event)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec())