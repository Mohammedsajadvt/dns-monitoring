# NetSentry — Wi-Fi Network Monitoring & DNS Threat Intelligence Platform

NetSentry is a cybersecurity platform designed to register Wi-Fi networks, discover connected devices, inspect and log DNS query activity in real-time, detect cybersecurity threats (phishing, DGA botnets, crypto-miners), and manage everything remotely via a modern **Web Admin Dashboard** and **Flutter Mobile Application**.

---

## 🌟 System Architecture

```
                                  ┌────────────────────────┐
                                  │   LAN Wi-Fi Clients    │
                                  │ (Phones, Laptops, IoT) │
                                  └───────────┬────────────┘
                                              │ DNS Queries (Port 53 / 5353)
                                              ▼
                                  ┌────────────────────────┐
                                  │ NetSentry Gateway Agent│
                                  │ (DNS Proxy + ARP Scan) │
                                  └───────────┬────────────┘
                                              │ HTTPS / WebSockets
                                              ▼
        ┌───────────────────────────────────────────────────────────────────────────┐
        │                   NetSentry FastAPI Cloud Backend                         │
        │  ├── MongoDB Atlas (Multi-Tenant, Indexes, Query Logs, Device Catalog)   │
        │  ├── Threat Heuristics Engine (Shannon Entropy DGA, Phishing, Blocklists) │
        │  ├── WebSocket Broadcast Engine (Real-time Stream)                        │
        │  └── CSV Audit Export & Analytics Aggregations                            │
        └──────────────────────────────┬────────────────────────────┬───────────────┘
                                       │                            │
                                       ▼                            ▼
                        ┌────────────────────────┐   ┌────────────────────────┐
                        │   Web Admin Dashboard  │   │   Flutter Mobile App   │
                        │ (Live Ticker, Charts)  │   │  (Cross-Platform APK)  │
                        └────────────────────────┘   └────────────────────────┘
```

---

## 📁 Repository Structure

- **`backend/`**: FastAPI REST API, MongoDB Atlas connector, JWT authentication, Shannon Entropy Threat Engine, and WebSocket broadcaster.
- **`web-dashboard/`**: Glassmorphic Cyber Intelligence Dashboard (HTML5 / ES6 / CSS / Chart.js / Lucide Icons).
- **`gateway-agent/`**: Lightweight cross-platform Python DNS Proxy, ARP device scanner, batch buffer sync engine, and simulation mode.
- **`mobile_app/`**: Full cross-platform Flutter application for iOS and Android with live stream, device inventory, and security alert manager.

---

## 🚀 Quick Start Guide

### 1. Start the Backend API & Web Dashboard

```bash
# In project root:
cd backend
python -m uvicorn app.main:app --app-dir . --host 0.0.0.0 --port 8000 --reload
```

- **Web Admin Dashboard**: Open [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Interactive API Docs (Swagger UI)**: Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

### 2. Run the Gateway Agent (DNS Sniffer / Proxy)

```bash
cd gateway-agent

# Option A: Run in Simulation Mode (Emulates multi-device LAN traffic)
python gateway_agent.py --simulate --network net_home_01

# Option B: Run as Local DNS Server (Requires admin on port 53 or custom port 5353)
python gateway_agent.py --port 5353 --network net_home_01
```

---

### 3. Run the Flutter Mobile App

```bash
cd mobile_app
flutter pub get
flutter run
```

> **Note for Mobile App Connection:**
> - In Android Emulator: Connects to `http://10.0.2.2:8000`
> - On Physical Phone: Tap the ⚙️ Settings icon in the app bar and enter your PC's Wi-Fi IP address (e.g., `http://192.168.1.100:8000`).

---

## 🛡️ Security & Threat Detection Capabilities

1. **Shannon Entropy DGA Detection**: Calculates character randomness entropy to detect malware command-and-control (C2) botnet domains (e.g. `xyzw981273918237alskdfj.biz`).
2. **Brand Impersonation & Phishing Lookalikes**: Flags suspicious typosquats and credential-harvesting patterns (`paypa1-security.com`, `apple-id-verify.com`).
3. **Cryptomining Signatures**: Blocks browser-based and endpoint miners (`coinhive`, `cryptoloot`, `webminepool`).
4. **Custom Domain Blocklist**: Allows immediate policy-based domain blocking across the network.
5. **CSV Export & Audit Trail**: Enables export of logs with user tracking for compliance.
