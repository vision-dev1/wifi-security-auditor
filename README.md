# WiFi Security Auditor

![WiFi Security Auditor](https://github.com/vision-dev1/wifi-security-auditor/blob/03c1955dc13773dc537cfb061c27594187d5c886/screenshot.png)

## Description

WiFi Security Auditor is a powerful network scanning tool designed to identify and analyze nearby Wi-Fi networks. It provides detailed information about network security, helping users understand potential vulnerabilities in their wireless environments. The tool features a modern web interface built with Flask, offering real-time scanning capabilities and security scoring.

## Features

- 🔍 **Network Discovery**: Scans and identifies nearby Wi-Fi networks
- 📊 **Detailed Analysis**: Shows SSID, BSSID, Signal Strength, Channel, and Encryption type
- 🛡️ **Security Scoring**: Rates networks as Secure ✅, Moderate ⚠️, or Vulnerable ❌
- 🖥️ **Modern Web Interface**: Sleek, responsive dashboard with cyber-themed design
- 📤 **Export Capabilities**: Export scan results as JSON or CSV files
- ⚡ **Real-time Scanning**: Progress indicators and loading animations
- 📱 **Responsive Design**: Works on both desktop and mobile devices

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/vision-dev1/wifi-security-auditor.git
   cd wifi-security-auditor
   ```

2. Install required dependencies:
   ```bash
   pip install flask
   ```

3. On Linux systems, you may need to install additional tools:
   ```bash
   sudo apt-get update
   sudo apt-get install net-tools wireless-tools
   ```

## Usage

1. Run the application:
   ```bash
   python3 wifi_auditor.py
   ```

2. Open your web browser and navigate to:
   ```
   http://localhost:5000
   ```

3. Click the "Scan Networks" button to begin scanning for nearby Wi-Fi networks.

4. View results in the interactive table and export as needed.

## Requirements

- Python 3.6+
- Flask
- System with Wi-Fi capability
- Appropriate permissions for network scanning

## Screenshots

![Dashboard](screenshots/dashboard.png)
*Main Dashboard Interface*

![Scan Results](screenshots/results.png)
*Network Scan Results with Security Scores*

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Legal Disclaimer

⚠️ **Important**: This tool is developed for **educational and authorized security auditing purposes only**.

Unauthorized scanning or network intrusion is illegal and strictly prohibited. The author assumes **no responsibility** for misuse of this tool.

Always ensure you have explicit permission before scanning networks that you do not own or operate.

## Author

**Vision KC**
- Website: [visionkc.com.np](https://visionkc.com.np)
- GitHub: [@vision-dev1](https://github.com/vision-dev1)

---

Made with ❤️ by Vision
