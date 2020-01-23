# probeMap

Updating for the Github code freeze.

Gather SSIDs (router names) from surrounding devices
and google-map them in a GUI interface.

Scapy sniffs packets.
Google maps are stored in the sqlite database.

Dependencies and How to Install

System and PyQt4
apt-get install:
build-essential wget git
python2.7-dev python-pip 
libxext-dev python-qt4 qt4-dev-tools 

pygmaps module
wget https://pygmaps.googlecode.com/files/pygmaps-0.1.1.tar.gz
tar -zxvf pygmaps-0.1.1.tar.gz
cd pygmaps-0.1.1 && python setup.py install

other modules
pip install -r requirements.txt


- TravisCI button w/state of build
- Quickstart documentation
