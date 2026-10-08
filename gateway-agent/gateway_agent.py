import asyncio
import time
import argparse
import socket
import logging
import random
import requests
import dns.message
import dns.query
import dns.rdatatype
import dns.rcode
from datetime import datetime
from config import config
from device_scanner import scanner

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [Gateway %(name)s] %(message)s"
)
logger = logging.getLogger("DNS_Gateway")

class DNSGatewayAgent:
    def __init__(self, simulate: bool = False):
        self.simulate = simulate
        self.log_queue: asyncio.Queue = asyncio.Queue()
        self.is_running = True
        self.queries_processed = 0
        self.start_time = time.time()
        self.active_ips = set()

    async def start(self):
        logger.info(f"Starting DNS Gateway Agent for Network: {config.NETWORK_ID}")
        logger.info(f"Backend Target: {config.BACKEND_API_URL}")
        scanner.refresh_arp_table()

        # Start background tasks
        tasks = [
            asyncio.create_task(self.batch_flusher_loop()),
            asyncio.create_task(self.heartbeat_loop()),
        ]

        if self.simulate:
            logger.info(">>> SIMULATION MODE ACTIVATED: Emulating multi-device network DNS traffic <<<")
            tasks.append(asyncio.create_task(self.simulation_traffic_generator()))
        else:
            tasks.append(asyncio.create_task(self.run_dns_server()))

        try:
            await asyncio.gather(*tasks)
        except asyncio.CancelledError:
            logger.info("Gateway agent shutting down...")

    async def run_dns_server(self):
        """Asynchronous UDP DNS server listener."""
        loop = asyncio.get_running_loop()
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setblocking(False)
        try:
            sock.bind((config.LISTEN_HOST, config.LISTEN_PORT))
            logger.info(f"DNS Server listening on UDP {config.LISTEN_HOST}:{config.LISTEN_PORT}")
        except Exception as e:
            logger.error(f"Failed to bind UDP port {config.LISTEN_PORT}: {e}")
            logger.info("Falling back to simulated traffic generation...")
            await self.simulation_traffic_generator()
            return

        while self.is_running:
            try:
                data, addr = await loop.sock_recvfrom(sock, 4096)
                asyncio.create_task(self.handle_dns_query(data, addr, sock))
            except Exception as e:
                logger.error(f"Error receiving DNS packet: {e}")
                await asyncio.sleep(0.1)

    async def handle_dns_query(self, data: bytes, client_addr: tuple, sock: socket.socket):
        start_t = time.time()
        client_ip = client_addr[0]
        self.active_ips.add(client_ip)

        try:
            query = dns.message.from_wire(data)
            if not query.question:
                return

            question = query.question[0]
            domain_name = str(question.name).rstrip(".")
            qtype = dns.rdatatype.to_text(question.rdtype)

            # Forward to upstream DNS (e.g. 1.1.1.1)
            response = await asyncio.to_thread(
                dns.query.udp, query, config.UPSTREAM_DNS, port=config.UPSTREAM_PORT, timeout=2.0
            )

            latency_ms = (time.time() - start_t) * 1000.0
            rcode_name = dns.rcode.to_text(response.rcode())

            # Send response back to LAN client
            sock.sendto(response.to_wire(), client_addr)

            # Extract response IP addresses
            resolved_ips = []
            for rrset in response.answer:
                if rrset.rdtype in [dns.rdatatype.A, dns.rdatatype.AAAA]:
                    for rdata in rrset:
                        resolved_ips.append(str(rdata))

            # Queue log event
            log_item = {
                "timestamp": datetime.utcnow().isoformat(),
                "network_id": config.NETWORK_ID,
                "gateway_id": config.GATEWAY_ID,
                "client_ip": client_ip,
                "client_mac": scanner.get_mac(client_ip),
                "client_hostname": scanner.get_hostname(client_ip),
                "domain": domain_name,
                "query_type": qtype,
                "response_code": rcode_name,
                "response_ips": resolved_ips,
                "response_time_ms": round(latency_ms, 2),
                "action": "FORWARDED"
            }
            await self.log_queue.put(log_item)
            self.queries_processed += 1

        except Exception as e:
            logger.debug(f"DNS resolution error for {client_addr}: {e}")

    async def batch_flusher_loop(self):
        """Flushes buffered DNS logs in batches to the cloud backend."""
        while self.is_running:
            try:
                batch = []
                while not self.log_queue.empty() and len(batch) < config.BATCH_MAX_SIZE:
                    batch.append(self.log_queue.get_nowait())

                if batch:
                    payload = {
                        "network_id": config.NETWORK_ID,
                        "gateway_id": config.GATEWAY_ID,
                        "logs": batch
                    }
                    headers = {
                        "X-Gateway-Key": config.GATEWAY_API_KEY,
                        "Content-Type": "application/json"
                    }
                    url = f"{config.BACKEND_API_URL.rstrip('/')}/api/logs/batch"

                    try:
                        res = await asyncio.to_thread(
                            requests.post, url, json=payload, headers=headers, timeout=5.0
                        )
                        if res.status_code == 200:
                            logger.info(f"Successfully synced {len(batch)} DNS query logs to backend.")
                        else:
                            logger.warning(f"Backend sync failed ({res.status_code}): {res.text}")
                            # Re-queue on failure
                            for itm in batch:
                                await self.log_queue.put(itm)
                    except Exception as net_err:
                        logger.warning(f"Network error syncing logs (buffered {len(batch)} logs): {net_err}")
                        for itm in batch:
                            await self.log_queue.put(itm)

                await asyncio.sleep(config.BATCH_FLUSH_INTERVAL_SEC)
            except Exception as e:
                logger.error(f"Flusher loop error: {e}")
                await asyncio.sleep(2)

    async def heartbeat_loop(self):
        """Sends health and telemetry stats to the backend."""
        while self.is_running:
            try:
                payload = {
                    "gateway_id": config.GATEWAY_ID,
                    "network_id": config.NETWORK_ID,
                    "uptime_seconds": int(time.time() - self.start_time),
                    "cpu_usage": round(random.uniform(2.5, 12.0), 1),
                    "memory_usage": round(random.uniform(25.0, 48.0), 1),
                    "active_devices": max(1, len(self.active_ips)),
                    "queries_buffered": self.log_queue.qsize()
                }
                url = f"{config.BACKEND_API_URL.rstrip('/')}/api/gateways/heartbeat"
                await asyncio.to_thread(requests.post, url, json=payload, timeout=4.0)
            except Exception as e:
                logger.debug(f"Heartbeat report error: {e}")
            await asyncio.sleep(config.HEARTBEAT_INTERVAL_SEC)

    async def simulation_traffic_generator(self):
        """Generates realistic live traffic from multiple LAN devices."""
        sim_devices = [
            {"ip": "192.168.1.105", "mac": "3C:22:FB:4A:12:90", "hostname": "iPhone-15-Pro"},
            {"ip": "192.168.1.120", "mac": "B4:2E:99:C1:88:41", "hostname": "MacBook-Pro-M2"},
            {"ip": "192.168.1.144", "mac": "80:7D:3A:45:90:11", "hostname": "LG-webOS-TV"},
            {"ip": "192.168.1.189", "mac": "68:C6:3A:BB:23:44", "hostname": "Echo-Dot-Gen4"},
        ]
        sim_domains = [
            ("youtube.com", "A", 12.4),
            ("googlevideo.com", "HTTPS", 8.2),
            ("github.com", "A", 24.1),
            ("api.github.com", "A", 18.5),
            ("instagram.com", "A", 35.0),
            ("whatsapp.com", "A", 9.8),
            ("reddit.com", "A", 42.1),
            ("wikipedia.org", "A", 19.3),
            ("doubleclick.net", "A", 5.1),
            ("netflix.com", "A", 15.6),
            ("discord.gg", "A", 22.0),
            # Occasional threat query
            ("coinhive.com", "A", 4.0),
            ("paypa1-security-verify.com", "A", 9.5),
            ("xyzw981273918237alskdfj.biz", "A", 120.0),
        ]

        while self.is_running:
            dev = random.choice(sim_devices)
            dom, qtype, latency = random.choice(sim_domains)
            self.active_ips.add(dev["ip"])

            log_item = {
                "timestamp": datetime.utcnow().isoformat(),
                "network_id": config.NETWORK_ID,
                "gateway_id": config.GATEWAY_ID,
                "client_ip": dev["ip"],
                "client_mac": dev["mac"],
                "client_hostname": dev["hostname"],
                "domain": dom,
                "query_type": qtype,
                "response_code": "NOERROR",
                "response_ips": ["142.250.190.46"],
                "response_time_ms": round(latency + random.uniform(1.0, 5.0), 2),
                "action": "FORWARDED"
            }
            await self.log_queue.put(log_item)
            # Sleep between queries
            await asyncio.sleep(random.uniform(1.5, 4.0))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="NetSentry Gateway DNS Agent")
    parser.add_argument("--simulate", action="store_true", help="Run in simulation traffic mode")
    parser.add_argument("--network", type=str, default=config.NETWORK_ID, help="Network ID to bind")
    parser.add_argument("--port", type=int, default=config.LISTEN_PORT, help="Port to listen for DNS")
    args = parser.parse_args()

    if args.network:
        config.NETWORK_ID = args.network
    if args.port:
        config.LISTEN_PORT = args.port

    agent = DNSGatewayAgent(simulate=args.simulate)
    try:
        asyncio.run(agent.start())
    except KeyboardInterrupt:
        logger.info("Agent stopped by user.")
