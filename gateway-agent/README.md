# NetSentry Gateway Agent & DNS Logger

This lightweight agent captures and logs local network DNS queries and synchronizes them securely with your NetSentry Cloud Backend and MongoDB Atlas database.

## Deployment Options

### 1. Run on Windows or Linux PC (DNS Server / Proxy Mode)
1. Install dependencies:
   ```bash
   pip install dnspython requests pydantic-settings python-dotenv
   ```
2. Start the agent:
   ```bash
   # Standard port 53 (requires administrator / root privileges)
   python gateway_agent.py --port 53 --network net_home_01

   # Or run with test simulation traffic:
   python gateway_agent.py --simulate --network net_home_01
   ```
3. Set your Wi-Fi router's primary DNS or client device's DNS server IP to this PC's local IP (e.g., `192.168.1.100`).

---

### 2. Run on Raspberry Pi / Linux Gateway
Run it as a persistent `systemd` service:
```ini
[Unit]
Description=NetSentry DNS Gateway Agent
After=network.target

[Service]
ExecStart=/usr/bin/python3 /opt/netsentry/gateway_agent.py --port 53 --network net_home_01
Restart=always
User=root

[Install]
WantedBy=multi-user.target
```

---

### 3. OpenWrt Router Native Integration
On OpenWrt routers with `dnsmasq`, you can either:
- Set `dnsmasq` upstream to this gateway (`server=192.168.1.100#5353`), OR
- Enable query logging in `/etc/config/dhcp`:
  ```bash
  uci set dhcp.@dnsmasq[0].logqueries='1'
  uci commit dhcp
  /etc/init.d/dnsmasq restart
  ```
  And stream `logread -f | grep dnsmasq` using our OpenWrt collector script.
