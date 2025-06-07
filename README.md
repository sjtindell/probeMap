# probeMap

A tool that gathers SSIDs (router names) from surrounding devices and displays them on a Google Maps interface.

## Features
- Scapy packet sniffing for SSID detection
- Google Maps integration with SQLite database storage
- GUI interface built with PyQt4

## Dependencies and Installation

### System Requirements
```bash
apt-get install build-essential wget git
apt-get install python2.7-dev python-pip 
apt-get install libxext-dev python-qt4 qt4-dev-tools 
```

### Python Dependencies
```bash
wget https://pygmaps.googlecode.com/files/pygmaps-0.1.1.tar.gz
tar -zxvf pygmaps-0.1.1.tar.gz
cd pygmaps-0.1.1 && python setup.py install

pip install -r requirements.txt
```

## TODO

- [ ] Add TravisCI integration with build status
- [ ] Add quickstart documentation
- [ ] Configure setup.py and set up package for pip installation
- [ ] Add logging module

- [ ] Add dates to mac_to_ssid table and display on widget
- [ ] Add query timer
- [ ] Add authentication key management:
  - [ ] Add page to enter auth key
  - [ ] Add page to get auth key
  - [ ] Implement secure storage

- [ ] Remove pygmaps middle step and drawing of HTML files (draw directly to DB)
- [ ] Add comprehensive test suite
- [ ] Optimize database operations:
  - [ ] Reduce database open operations
  - [ ] Move more operations to sqlwrap
  - [ ] Improve manage.py functionality

- [ ] General code cleanup
- [ ] Reduce module count and improve organization
- [ ] Add automatic wireless card monitor mode configuration
