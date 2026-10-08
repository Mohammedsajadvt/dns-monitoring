import subprocess
import re
import socket
import platform
from typing import Dict, Optional

class DeviceScanner:
    def __init__(self):
        self.arp_cache: Dict[str, str] = {} # IP -> MAC
        self.hostname_cache: Dict[str, str] = {} # IP -> Hostname

    def refresh_arp_table(self):
        """Parse system ARP table (cross-platform Windows & Linux)."""
        system = platform.system().lower()
        try:
            if system == "windows":
                output = subprocess.check_output(["arp", "-a"], text=True, stderr=subprocess.DEVNULL)
                for line in output.splitlines():
                    match = re.search(r'([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)\s+([0-9a-fA-F\-]{17})', line)
                    if match:
                        ip = match.group(1)
                        mac = match.group(2).replace("-", ":").upper()
                        self.arp_cache[ip] = mac
            else:
                # Linux / OpenWrt
                output = subprocess.check_output(["arp", "-n"], text=True, stderr=subprocess.DEVNULL)
                for line in output.splitlines():
                    parts = line.split()
                    if len(parts) >= 4 and ":" in parts[2]:
                        self.arp_cache[parts[0]] = parts[2].upper()
        except Exception:
            pass

    def get_mac(self, ip: str) -> str:
        if ip in self.arp_cache:
            return self.arp_cache[ip]
        if ip == "127.0.0.1" or ip == "localhost":
            return "00:00:00:00:00:00"
        return "Unknown"

    def get_hostname(self, ip: str) -> str:
        if ip in self.hostname_cache:
            return self.hostname_cache[ip]
        if ip == "127.0.0.1":
            return "Gateway Host"
        try:
            name, _, _ = socket.gethostbyaddr(ip)
            self.hostname_cache[ip] = name
            return name
        except Exception:
            self.hostname_cache[ip] = f"Device-{ip.replace('.', '-')}"
            return self.hostname_cache[ip]

scanner = DeviceScanner()
