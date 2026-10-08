from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

# User Models
class UserCreate(BaseModel):
    email: str
    password: str
    full_name: str
    role: str = "admin" # admin, viewer

class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: Optional[str] = None
    email: str
    full_name: str
    role: str
    created_at: datetime

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

# Network Models
class NetworkCreate(BaseModel):
    name: str
    location: Optional[str] = "Main Office / Home"
    description: Optional[str] = ""
    subnet: Optional[str] = "192.168.1.0/24"

class NetworkUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
    subnet: Optional[str] = None

class NetworkResponse(BaseModel):
    network_id: str
    name: str
    location: str
    description: str
    subnet: str
    created_at: datetime
    device_count: int = 0
    gateway_online: bool = False
    last_active: Optional[datetime] = None

# Gateway Models
class GatewayRegister(BaseModel):
    network_id: str
    gateway_name: str
    gateway_type: str = "linux_pc" # linux_pc, router_openwrt, raspberry_pi, windows_dns_proxy
    ip_address: Optional[str] = "127.0.0.1"
    version: Optional[str] = "1.0.0"

class GatewayHeartbeat(BaseModel):
    gateway_id: str
    network_id: str
    uptime_seconds: int = 0
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    active_devices: int = 0
    queries_buffered: int = 0

class GatewayResponse(BaseModel):
    gateway_id: str
    network_id: str
    gateway_name: str
    gateway_type: str
    ip_address: str
    api_key: str
    is_online: bool
    last_heartbeat: Optional[datetime] = None
    version: str

# Device Models
class DeviceUpdate(BaseModel):
    friendly_name: Optional[str] = None
    device_type: Optional[str] = None # phone, laptop, smart_tv, iot, router, unknown
    is_blocked: Optional[bool] = None
    notes: Optional[str] = None

class DeviceResponse(BaseModel):
    network_id: str
    ip: str
    mac: Optional[str] = "Unknown"
    hostname: Optional[str] = "Unknown Host"
    friendly_name: Optional[str] = None
    device_type: str = "unknown"
    vendor: Optional[str] = "Unknown"
    first_seen: datetime
    last_seen: datetime
    is_online: bool = True
    is_blocked: bool = False
    total_queries: int = 0
    notes: Optional[str] = ""

# DNS Log Models
class DNSQueryIngest(BaseModel):
    timestamp: Optional[datetime] = None
    network_id: str
    gateway_id: Optional[str] = "gw_default"
    client_ip: str
    client_mac: Optional[str] = "00:00:00:00:00:00"
    client_hostname: Optional[str] = None
    domain: str
    query_type: str = "A" # A, AAAA, HTTPS, CNAME, PTR, TXT, MX
    response_code: str = "NOERROR" # NOERROR, NXDOMAIN, SERVFAIL, BLOCKED
    response_ips: List[str] = []
    response_time_ms: float = 0.0
    action: str = "FORWARDED" # FORWARDED, BLOCKED, CACHED

class DNSLogBatchIngest(BaseModel):
    network_id: str
    gateway_id: str
    logs: List[DNSQueryIngest]

class DNSLogResponse(BaseModel):
    id: str
    timestamp: datetime
    network_id: str
    gateway_id: str
    client_ip: str
    client_mac: str
    client_name: str
    domain: str
    category: str = "General" # Search, Social Media, Video Streaming, Work, Ads/Tracking, Suspicious, Malware
    query_type: str
    response_code: str
    response_ips: List[str]
    response_time_ms: float
    action: str
    is_threat: bool = False
    threat_type: Optional[str] = None
    threat_severity: Optional[str] = None # low, medium, high, critical

# Threat Alert Models
class ThreatAlertResponse(BaseModel):
    id: str
    network_id: str
    timestamp: datetime
    domain: str
    client_ip: str
    client_name: str
    threat_type: str # DGA, Phishing, Malware, Cryptominer, Suspicious TLD, Blocklisted
    severity: str # low, medium, high, critical
    details: str
    is_resolved: bool = False

# Blocklist
class BlockedDomainCreate(BaseModel):
    domain: str
    network_id: str
    category: str = "Manual Block"
    reason: Optional[str] = "Administrative policy"

# Analytics Models
class QuickStats(BaseModel):
    total_queries_today: int
    active_devices_count: int
    threats_blocked_today: int
    top_domains: List[Dict[str, Any]]
    query_timeline: List[Dict[str, Any]]
    category_distribution: List[Dict[str, Any]]
    threat_breakdown: List[Dict[str, Any]]
