#!/usr/bin/env python3

import subprocess
import re
import sys

def test_tcpdump(interface='en0'):
    print(f"Testing tcpdump on interface {interface}")
    print("Press Ctrl+C to stop")
    
    # tcpdump command to capture probe requests
    cmd = ['sudo', 'tcpdump', '-i', interface, '-I', '-n', '-l', '-e', 'type mgt subtype probe-req']
    
    try:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Updated regex to match the actual tcpdump output format
        probe_regex = re.compile(r'SA:(\w\w:\w\w:\w\w:\w\w:\w\w:\w\w).*Probe Request \(([^)]*)\)')
        
        while True:
            line = process.stdout.readline()
            if not line:
                break
            
            # Print raw line for debugging
            print(f"Raw: {line.strip()}")
            
            match = probe_regex.search(line)
            if match:
                mac, ssid = match.groups()
                if ssid:  # Only print if SSID is not empty
                    print(f"Found SSID: {ssid} from MAC: {mac}")
            
    except KeyboardInterrupt:
        print("\nStopping capture...")
    finally:
        process.terminate()

if __name__ == '__main__':
    interface = sys.argv[1] if len(sys.argv) > 1 else 'en0'
    test_tcpdump(interface) 