import asyncio
import random
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings
from app.threat_engine import inspect_domain_threat
from app.auth import get_password_hash

async def seed():
    print(f"Connecting to MongoDB Atlas at {settings.MONGODB_URI[:30]}...")
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    db = client[settings.DATABASE_NAME]
    
    # 1. Ensure Admin User
    await db.users.update_one(
        {"email": "admin@netsentry.io"},
        {"$set": {
            "user_id": "user_admin_01",
            "email": "admin@netsentry.io",
            "password_hash": get_password_hash("Admin@12345"),
            "full_name": "Sajad Security Admin",
            "role": "admin",
            "created_at": datetime.utcnow()
        }},
        upsert=True
    )
    print("[+] Admin user upserted: admin@netsentry.io / Admin@12345")

        
    # 2. Seed Networks
    net_1 = {
        "network_id": "net_home_01",
        "name": "Smart Home Wi-Fi Mesh",
        "location": "Main Residence - Kerala",
        "description": "5GHz Mesh Network with IoT isolation",
        "subnet": "192.168.1.0/24",
        "created_at": datetime.utcnow() - timedelta(days=15)
    }
    net_2 = {
        "network_id": "net_office_02",
        "name": "CyberSec Lab & Office Gateway",
        "location": "Innovation Hub HQ",
        "description": "Enterprise Linux DNS Proxy with Threat Filtering",
        "subnet": "10.0.10.0/24",
        "created_at": datetime.utcnow() - timedelta(days=10)
    }
    await db.networks.update_one({"network_id": net_1["network_id"]}, {"$set": net_1}, upsert=True)
    await db.networks.update_one({"network_id": net_2["network_id"]}, {"$set": net_2}, upsert=True)
    print("[+] Networks seeded.")

    # 3. Seed Gateways
    gw_1 = {
        "gateway_id": "gw_home_router",
        "network_id": "net_home_01",
        "gateway_name": "OpenWrt Core Router",
        "gateway_type": "router_openwrt",
        "ip_address": "192.168.1.1",
        "api_key": "gwk_home_live_token_7788",
        "version": "1.2.0",
        "last_heartbeat": datetime.utcnow()
    }
    gw_2 = {
        "gateway_id": "gw_linux_box",
        "network_id": "net_office_02",
        "gateway_name": "Ubuntu Sentry Gateway",
        "gateway_type": "linux_pc",
        "ip_address": "10.0.10.1",
        "api_key": "gwk_office_live_token_9900",
        "version": "1.2.0",
        "last_heartbeat": datetime.utcnow()
    }
    await db.gateways.update_one({"gateway_id": gw_1["gateway_id"]}, {"$set": gw_1}, upsert=True)
    await db.gateways.update_one({"gateway_id": gw_2["gateway_id"]}, {"$set": gw_2}, upsert=True)

    # 4. Seed Devices
    sample_devices = [
        {"network_id": "net_home_01", "ip": "192.168.1.105", "mac": "3C:22:FB:4A:12:90", "hostname": "iPhone-15-Pro", "friendly_name": "Sajad's iPhone", "device_type": "phone", "vendor": "Apple Inc."},
        {"network_id": "net_home_01", "ip": "192.168.1.120", "mac": "B4:2E:99:C1:88:41", "hostname": "MacBook-Pro-M2", "friendly_name": "Dev Workstation", "device_type": "laptop", "vendor": "Apple Inc."},
        {"network_id": "net_home_01", "ip": "192.168.1.144", "mac": "80:7D:3A:45:90:11", "hostname": "LG-webOS-TV", "friendly_name": "Living Room OLED TV", "device_type": "smart_tv", "vendor": "LG Electronics"},
        {"network_id": "net_home_01", "ip": "192.168.1.189", "mac": "68:C6:3A:BB:23:44", "hostname": "Echo-Dot-Gen4", "friendly_name": "Alexa Smart Speaker", "device_type": "iot", "vendor": "Amazon"},
        {"network_id": "net_home_01", "ip": "192.168.1.210", "mac": "E4:5F:01:77:88:22", "hostname": "RaspberryPi-Gateway", "friendly_name": "Pi Sentry Logger", "device_type": "router", "vendor": "Raspberry Pi Trading"},
        {"network_id": "net_office_02", "ip": "10.0.10.45", "mac": "00:1A:2B:3C:4D:5E", "hostname": "Security-Audit-Box", "friendly_name": "SecOps Kali Linux", "device_type": "laptop", "vendor": "Dell Inc."},
        {"network_id": "net_office_02", "ip": "10.0.10.78", "mac": "AC:DE:48:11:22:33", "hostname": "Android-Pixel-8", "friendly_name": "QA Testing Phone", "device_type": "phone", "vendor": "Google LLC"},
    ]
    
    for dev in sample_devices:
        dev["first_seen"] = datetime.utcnow() - timedelta(days=7)
        dev["last_seen"] = datetime.utcnow() - timedelta(minutes=random.randint(1, 40))
        dev["is_blocked"] = False
        dev["total_queries"] = random.randint(150, 4800)
        await db.devices.update_one({"network_id": dev["network_id"], "ip": dev["ip"]}, {"$set": dev}, upsert=True)
    print("[+] Devices seeded.")

    # 5. Seed DNS Query Logs & Threats
    sample_domains = [
        ("youtube.com", "A", 12.4),
        ("googlevideo.com", "HTTPS", 8.2),
        ("github.com", "A", 24.1),
        ("api.github.com", "A", 18.5),
        ("instagram.com", "A", 35.0),
        ("fbcdn.net", "HTTPS", 14.2),
        ("whatsapp.com", "A", 9.8),
        ("whatsapp.net", "A", 11.2),
        ("reddit.com", "A", 42.1),
        ("wikipedia.org", "A", 19.3),
        ("doubleclick.net", "A", 5.1),
        ("googleadservices.com", "A", 6.2),
        ("stackoverflow.com", "A", 31.0),
        ("netflix.com", "A", 15.6),
        ("discord.gg", "A", 22.0),
        # Simulated Threats
        ("coinhive.com", "A", 4.0),
        ("paypa1-security-verify.com", "A", 9.5),
        ("xyzw981273918237alskdfj.biz", "A", 120.0),
        ("crypto-webminer-pool.xyz", "A", 15.0),
    ]

    now = datetime.utcnow()
    logs_to_insert = []
    alerts_to_insert = []
    
    # Check if logs already exist
    existing_logs_count = await db.dns_logs.count_documents({})
    if existing_logs_count < 20:
        for i in range(120):
            time_offset = timedelta(minutes=i * 12, seconds=random.randint(1, 55))
            log_time = now - time_offset
            
            dev = random.choice(sample_devices)
            domain_choice, q_type, latency = random.choice(sample_domains)
            
            is_threat, threat_type, severity, category = inspect_domain_threat(domain_choice)
            action = "BLOCKED" if is_threat else ("CACHED" if random.random() < 0.25 else "FORWARDED")
            
            log_id = f"log_demo_{i}_{random.randint(1000, 9999)}"
            log_doc = {
                "log_id": log_id,
                "timestamp": log_time,
                "network_id": dev["network_id"],
                "gateway_id": "gw_home_router" if dev["network_id"] == "net_home_01" else "gw_linux_box",
                "client_ip": dev["ip"],
                "client_mac": dev["mac"],
                "client_name": dev["friendly_name"],
                "domain": domain_choice,
                "category": category,
                "query_type": q_type,
                "response_code": "BLOCKED" if action == "BLOCKED" else "NOERROR",
                "response_ips": ["142.250.190.46"] if not is_threat else ["0.0.0.0"],
                "response_time_ms": latency + random.uniform(1.0, 10.0),
                "action": action,
                "is_threat": is_threat,
                "threat_type": threat_type,
                "threat_severity": severity
            }
            logs_to_insert.append(log_doc)
            
            if is_threat and len(alerts_to_insert) < 15:
                alerts_to_insert.append({
                    "alert_id": f"alert_demo_{i}",
                    "network_id": dev["network_id"],
                    "timestamp": log_time,
                    "domain": domain_choice,
                    "client_ip": dev["ip"],
                    "client_name": dev["friendly_name"],
                    "threat_type": threat_type,
                    "severity": severity or "medium",
                    "details": f"High risk query identified: {domain_choice} (Heuristic engine trigger)",
                    "is_resolved": random.choice([True, False])
                })
                
        if logs_to_insert:
            await db.dns_logs.insert_many(logs_to_insert)
            print(f"[+] Inserted {len(logs_to_insert)} DNS query logs.")
        if alerts_to_insert:
            await db.threat_alerts.insert_many(alerts_to_insert)
            print(f"[+] Inserted {len(alerts_to_insert)} Threat Alerts.")
            
    client.close()
    print("[OK] Database seeding completed successfully!")

if __name__ == "__main__":
    asyncio.run(seed())
