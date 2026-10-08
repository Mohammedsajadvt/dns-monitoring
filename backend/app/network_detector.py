import subprocess
import platform
import socket
import logging

logger = logging.getLogger("dns_monitoring.network_detector")

def detect_current_wifi_network():
    """
    Automatically detects the connected Wi-Fi SSID / Active Network profile,
    local subnet and gateway IP address on Windows, Linux, and macOS.
    """
    system = platform.system()
    network_name = "Primary Wi-Fi Network"
    subnet = "192.168.1.0/24"
    location = "Local Gateway"

    # 1. Detect local IP and Subnet
    local_ip = "192.168.1.1"
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        ip_parts = local_ip.split(".")
        if len(ip_parts) == 4:
            subnet = f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}.0/24"
            location = f"{local_ip} Gateway"
    except Exception as e:
        logger.debug(f"Could not determine local IP: {e}")

    # 2. Detect Wi-Fi SSID / Network Name based on OS
    if system == "Windows":
        # Check Wireless Interface SSID
        try:
            wlan_out = subprocess.check_output(
                ["netsh", "wlan", "show", "interfaces"],
                text=True,
                stderr=subprocess.DEVNULL,
                timeout=2
            )
            for line in wlan_out.splitlines():
                if "SSID" in line and "BSSID" not in line:
                    parts = line.split(":")
                    if len(parts) > 1:
                        ssid = parts[1].strip()
                        if ssid:
                            network_name = f"{ssid} (Wi-Fi)"
                            location = f"Wireless AP ({local_ip})"
                            break
        except Exception:
            pass

        # If not Wi-Fi, check Active Connection Profile (e.g. Airtel_6G, JioFiber, Ethernet)
        if network_name == "Primary Wi-Fi Network":
            try:
                ps_cmd = "Get-NetConnectionProfile | Select-Object -ExpandProperty Name"
                out = subprocess.check_output(
                    ["powershell", "-NoProfile", "-Command", ps_cmd],
                    text=True,
                    stderr=subprocess.DEVNULL,
                    timeout=3
                ).strip()
                if out:
                    lines = [l.strip() for l in out.splitlines() if l.strip()]
                    if lines:
                        detected_name = lines[0]
                        network_name = f"{detected_name} (Connected Wi-Fi)"
                        location = f"{local_ip} LAN"
            except Exception:
                pass

    elif system == "Linux":
        try:
            ssid = subprocess.check_output(["iwgetid", "-r"], text=True, stderr=subprocess.DEVNULL, timeout=2).strip()
            if ssid:
                network_name = f"{ssid} (Wi-Fi)"
                location = f"Wireless AP ({local_ip})"
        except Exception:
            pass

    elif system == "Darwin": # macOS
        try:
            airport_cmd = "/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport -I"
            out = subprocess.check_output(airport_cmd.split(), text=True, stderr=subprocess.DEVNULL, timeout=2)
            for line in out.splitlines():
                if " SSID:" in line:
                    ssid = line.split(":")[1].strip()
                    if ssid:
                        network_name = f"{ssid} (Wi-Fi)"
                        break
        except Exception:
            pass

    return {
        "name": network_name,
        "location": location,
        "subnet": subnet
    }
