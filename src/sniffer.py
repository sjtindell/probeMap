#!/usr/bin/env python3

import os
import sys
import platform
import subprocess
import threading
import re
import signal
from sqlwrap import Database

class BaseSniffer:
    def __init__(self, interface):
        self.interface = interface
        self.running = False
        self.thread = None
        self.process = None

    def start(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._run)
            self.thread.daemon = True
            self.thread.start()

    def stop(self):
        self.running = False
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=1)
            except:
                try:
                    self.process.kill()
                except:
                    pass
        if self.thread:
            self.thread.join(timeout=1)

    def _run(self):
        raise NotImplementedError

class MacSniffer(BaseSniffer):
    def _run(self):
        try:
            cmd = ['tcpdump', 
                   '-i', self.interface,
                   '-I',  # Monitor mode
                   '-n',  # Don't convert addresses to names
                   '-l',  # Line buffered
                   '-e',  # Print link-level header
                   '-t',  # Don't print timestamp
                   'type mgt subtype probe-req']  # Only probe requests
            
            print(f"Starting tcpdump with command: {' '.join(cmd)}")
            
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                preexec_fn=os.setsid
            )
            
            probe_regex = re.compile(r'SA:(\w\w:\w\w:\w\w:\w\w:\w\w:\w\w).*Probe Request \(([^)]*)\)')
            
            while self.running:
                line = self.process.stdout.readline()
                if not line:
                    break
                
                # Print all probe requests
                if "Probe Request" in line:
                    print(line.strip())
                
                match = probe_regex.search(line)
                if match:
                    mac, ssid = match.groups()
                    if ssid:
                        print(f"Found SSID: {ssid} from MAC: {mac}")
                        try:
                            with Database('probemap.db') as db:
                                db.insert_mac_ssid(mac, ssid)
                                print(f"Added to database: {mac} -> {ssid}")
                        except Exception as e:
                            print(f"Database error: {e}")
            
        except Exception as e:
            print(f"Error in tcpdump capture: {e}")
        finally:
            self.running = False
            if self.process:
                try:
                    os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
                except:
                    pass

class LinuxSniffer(BaseSniffer):
    def _run(self):
        try:
            from scapy.all import sniff, Dot11
            
            def check_packet(packet):
                if (packet.haslayer(Dot11) and
                    packet.type == 0 and
                    packet.subtype == 8 and
                    packet.info and
                    '\\x00' not in repr(packet.info) and
                    '\\x82\\x04\\x0b\\x16\\x0c\\x12\\x18$' not in repr(packet.info)):
                    
                    print(f"Found SSID: {packet.info}")
                    with Database('probemap.db') as db:
                        if packet.info not in [str(ssid) for mac, ssid in db.ssids]:
                            db.insert_mac_ssid(packet.addr2, packet.info)

            sniff(iface=self.interface, prn=check_packet, store=0)
            
        except Exception as e:
            print(f"Error in Scapy capture: {e}")
            self.running = False

def create_sniffer(interface):
    system = platform.system().lower()
    if system == 'darwin':
        return MacSniffer(interface)
    elif system == 'linux':
        return LinuxSniffer(interface)
    else:
        raise NotImplementedError(f"Unsupported operating system: {system}")

def watch(interface):
    sniffer = create_sniffer(interface)
    sniffer.start()
    return sniffer


if __name__ == '__main__':
    watch('en0')
