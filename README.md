# probeMap

A tool that gathers SSIDs (router names) from probe requests broadcast by 
surrounding devices and displays them on a Google Maps interface.

## macOS Quickstart

1. Create and activate a virtual environment:
   ```bash
   uv venv
   source venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   uv pip install -r requirements.txt
   ```

3. Install pygmaps (from Google Code archive):
   ```bash
   curl -LO https://storage.googleapis.com/google-code-archive-source/v2/code.google.com/pygmaps/source-archive.zip
   unzip source-archive.zip
   cd pygmaps/trunk
   python setup.py install
   cd ../..
   ```

4. Run the application:
   ```bash
   sudo python src/gui.py
   ```

Note: You'll need to run the application with sudo privileges to access the wireless interface in monitor mode.

## TODO

### High Priority
- [ ] Add TravisCI integration with build status
- [ ] Add quickstart documentation
- [ ] Configure setup.py and set up package for pip installation
- [ ] Add logging module
- [ ] Add unit tests

### Features
- [ ] Add dates to mac_to_ssid table and display on widget
- [ ] Add query timer
- [ ] Add authentication key management:
  - [ ] Add page to enter auth key
  - [ ] Add page to get auth key
  - [ ] Implement secure storage

### Technical Improvements
- [ ] Remove pygmaps middle step and drawing of HTML files (draw directly to DB)
- [ ] Optimize database operations:
  - [ ] Reduce database open operations
  - [ ] Move more operations to sqlwrap
  - [ ] Improve manage.py functionality

### Code Quality
- [ ] General code cleanup
- [ ] Reduce module count and improve organization
- [ ] Add automatic wireless card monitor mode configuration
