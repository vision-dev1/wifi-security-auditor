import os
import json
import csv
import time
import threading
from datetime import datetime
from flask import Flask, render_template, jsonify, send_file, request
import subprocess
import platform
import webbrowser

app = Flask(__name__)

# Global variable to store scan results
scan_results = []
scan_in_progress = False

def get_security_score(encryption):
    """Calculate security score based on encryption type"""
    if encryption == "WPA2" or encryption == "WPA3":
        return "Secure ✅"
    elif encryption == "WPA":
        return "Moderate ⚠️"
    elif encryption == "WEP":
        return "Vulnerable ❌"
    elif encryption == "Open":
        return "Vulnerable ❌"
    else:
        return "Unknown"

def scan_wifi_networks_nmcli():
    """Scan for WiFi networks using nmcli on Linux"""
    global scan_results, scan_in_progress
    
    scan_in_progress = True
    
    try:
        # First, rescan to refresh the list
        try:
            subprocess.run(['nmcli', 'device', 'wifi', 'rescan'], 
                          capture_output=True, text=True, timeout=10)
        except:
            # If rescan fails, continue anyway
            pass
        
        # Scan for networks with the required fields
        result = subprocess.run(['nmcli', '-f', 'SSID,SECURITY,SIGNAL,CHAN', 'device', 'wifi', 'list'], 
                              capture_output=True, text=True, timeout=15)
        
        if result.returncode == 0:
            networks = []
            lines = result.stdout.strip().split('\n')
            
            # Skip the header line
            if len(lines) > 1:
                data_lines = lines[1:]  # Skip header
                
                for line in data_lines:
                    if line.strip():
                        # Handle the case where SSID might be empty (hidden network)
                        # The output format is space-separated, but SSID can contain spaces
                        # We'll parse from the end since SECURITY, SIGNAL, CHAN are single values
                        
                        # Split the line into parts
                        parts = line.split()
                        if len(parts) >= 4:
                            # Extract the last 3 fields (CHAN, SIGNAL, SECURITY)
                            chan = parts[-1]
                            signal = parts[-2]
                            security = parts[-3]
                            
                            # Everything else is the SSID
                            ssid_parts = parts[:-3]
                            ssid = ' '.join(ssid_parts) if ssid_parts else ''
                            
                            # Handle hidden SSIDs (empty or '--')
                            if not ssid or ssid == '--':
                                ssid = '<Hidden Network>'
                            
                            network = {
                                'SSID': ssid,
                                'BSSID': 'N/A',
                                'Channel': chan,
                                'SignalStrength': f"{signal}%",
                                'Encryption': security if security != '--' else 'Open',
                                'SecurityScore': get_security_score(security if security != '--' else 'Open')
                            }
                            networks.append(network)
                        elif len(parts) == 3:
                            # Case where SSID is empty
                            chan = parts[-1]
                            signal = parts[-2]
                            security = parts[-3]
                            
                            network = {
                                'SSID': '<Hidden Network>',
                                'BSSID': 'N/A',
                                'Channel': chan,
                                'SignalStrength': f"{signal}%",
                                'Encryption': security if security != '--' else 'Open',
                                'SecurityScore': get_security_score(security if security != '--' else 'Open')
                            }
                            networks.append(network)
            
            # Handle case when no networks are found
            if not networks:
                networks.append({
                    'SSID': 'No Wi-Fi networks detected',
                    'BSSID': 'N/A',
                    'Channel': 'N/A',
                    'SignalStrength': 'N/A',
                    'Encryption': 'N/A',
                    'SecurityScore': 'N/A'
                })
            
            scan_results = networks
        else:
            # If nmcli fails, show appropriate error
            scan_results = [{
                'SSID': 'Scan Failed',
                'BSSID': 'N/A',
                'Channel': 'N/A',
                'SignalStrength': 'N/A',
                'Encryption': 'N/A',
                'SecurityScore': 'N/A',
                'Error': 'Unable to scan networks. Make sure NetworkManager is running and you have the necessary permissions.'
            }]
            
    except Exception as e:
        scan_results = [{
            'SSID': 'Error',
            'BSSID': 'N/A',
            'Channel': 'N/A',
            'SignalStrength': 'N/A',
            'Encryption': 'N/A',
            'SecurityScore': 'N/A',
            'Error': str(e)
        }]
    
    scan_in_progress = False
    return scan_results

def scan_wifi_networks():
    """Scan for WiFi networks using system commands"""
    global scan_results, scan_in_progress
    
    scan_in_progress = True
    
    try:
        # Try different methods based on OS
        system = platform.system()
        
        if system == "Linux":
            # Use our new nmcli implementation
            return scan_wifi_networks_nmcli()
                
        elif system == "Darwin":  # macOS
            try:
                result = subprocess.run(['/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport', '-s'], 
                                      capture_output=True, text=True, timeout=15)
                if result.returncode == 0:
                    networks = []
                    lines = result.stdout.strip().split('\n')[1:]  # Skip header
                    for line in lines:
                        if line.strip():
                            parts = line.split()
                            if len(parts) >= 5:
                                network = {
                                    'SSID': parts[0],
                                    'BSSID': ':'.join(parts[1:7]),
                                    'Channel': parts[7],
                                    'SignalStrength': f"{parts[8]}%",
                                    'Encryption': 'Unknown',  # Hard to determine on macOS
                                    'SecurityScore': 'Unknown'
                                }
                                networks.append(network)
                    scan_results = networks
                    scan_in_progress = False
                    return networks
            except:
                pass
                
        # If all methods fail
        scan_results = [{
            'SSID': 'Scan Failed',
            'BSSID': 'N/A',
            'Channel': 'N/A',
            'SignalStrength': 'N/A',
            'Encryption': 'N/A',
            'SecurityScore': 'N/A',
            'Error': 'Unable to scan networks. Make sure you have the necessary permissions.'
        }]
        
    except Exception as e:
        scan_results = [{
            'SSID': 'Error',
            'BSSID': 'N/A',
            'Channel': 'N/A',
            'SignalStrength': 'N/A',
            'Encryption': 'N/A',
            'SecurityScore': 'N/A',
            'Error': str(e)
        }]
    
    scan_in_progress = False
    return scan_results

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scan')
def scan():
    global scan_in_progress
    
    # Start scanning in a separate thread
    if not scan_in_progress:
        scan_thread = threading.Thread(target=scan_wifi_networks)
        scan_thread.start()
    
    return jsonify({'status': 'started'})

@app.route('/results')
def results():
    global scan_results, scan_in_progress
    return jsonify({
        'results': scan_results,
        'in_progress': scan_in_progress
    })

@app.route('/export/<format>')
def export_results(format):
    global scan_results
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if format == 'json':
        filename = f'results/scan_results_{timestamp}.json'
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w') as f:
            json.dump(scan_results, f, indent=2)
        return send_file(filename, as_attachment=True)
    
    elif format == 'csv':
        filename = f'results/scan_results_{timestamp}.csv'
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w', newline='') as f:
            if scan_results:
                writer = csv.DictWriter(f, fieldnames=scan_results[0].keys())
                writer.writeheader()
                writer.writerows(scan_results)
        return send_file(filename, as_attachment=True)
    
    return jsonify({'error': 'Invalid format'}), 400

if __name__ == '__main__':
    # Function to open browser after a short delay
    def open_browser():
        time.sleep(2)  # Wait for the server to start
        webbrowser.open('http://localhost:5000')
    
    # Start the browser opening in a separate thread
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    app.run(host='0.0.0.0', port=5000, debug=True)