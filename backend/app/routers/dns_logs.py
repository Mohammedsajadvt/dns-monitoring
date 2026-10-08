import uuid
import re
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, Query, BackgroundTasks
from app.database import get_database
from app.models import DNSQueryIngest, DNSLogBatchIngest, DNSLogResponse
from app.threat_engine import inspect_domain_threat
from app.websocket_manager import ws_manager
from app.auth import get_current_user_optional, verify_gateway_api_key
from app.config import settings

router = APIRouter(prefix="/api/logs", tags=["DNS Logs"])

async def process_and_save_query(db, log: DNSQueryIngest):
    log_time = log.timestamp or datetime.utcnow()
    clean_domain = log.domain.lower().strip().rstrip(".")
    
    # Get custom blocked domains for this network
    blocked_cursor = db.blocked_domains.find({"network_id": log.network_id})
    blocked_docs = await blocked_cursor.to_list(length=500)
    blocked_set = {b["domain"].lower() for b in blocked_docs}
    
    is_threat, threat_type, severity, category = inspect_domain_threat(clean_domain, blocked_set)
    action = "BLOCKED" if is_threat else (log.action or "FORWARDED")
    
    # Fetch device friendly name if available
    dev = await db.devices.find_one({"network_id": log.network_id, "ip": log.client_ip})
    client_name = log.client_hostname or log.client_ip
    if dev and dev.get("friendly_name"):
        client_name = dev["friendly_name"]
        
    log_id = str(uuid.uuid4())
    log_doc = {
        "log_id": log_id,
        "timestamp": log_time,
        "network_id": log.network_id,
        "gateway_id": log.gateway_id or "gw_default",
        "client_ip": log.client_ip,
        "client_mac": log.client_mac or "Unknown",
        "client_name": client_name,
        "domain": clean_domain,
        "category": category,
        "query_type": log.query_type or "A",
        "response_code": "BLOCKED" if action == "BLOCKED" else (log.response_code or "NOERROR"),
        "response_ips": log.response_ips or [],
        "response_time_ms": float(log.response_time_ms or 0.0),
        "action": action,
        "is_threat": is_threat,
        "threat_type": threat_type,
        "threat_severity": severity
    }
    
    # Insert log
    await db.dns_logs.insert_one(log_doc)
    
    # Update device catalog
    device_update = {
        "$set": {
            "network_id": log.network_id,
            "ip": log.client_ip,
            "mac": log.client_mac or "Unknown",
            "last_seen": log_time
        },
        "$setOnInsert": {
            "hostname": log.client_hostname or f"Device-{log.client_ip.replace('.', '-')}",
            "friendly_name": None,
            "device_type": "laptop" if "192.168" in log.client_ip else "phone",
            "first_seen": log_time,
            "is_blocked": False
        },
        "$inc": {"total_queries": 1}
    }
    if log.client_hostname:
        device_update["$set"]["hostname"] = log.client_hostname
        
    await db.devices.update_one(
        {"network_id": log.network_id, "ip": log.client_ip},
        device_update,
        upsert=True
    )
    
    # Broadcast device update
    dev_doc = await db.devices.find_one({"network_id": log.network_id, "ip": log.client_ip})
    if dev_doc:
        dev_payload = {
            "network_id": dev_doc["network_id"],
            "ip": dev_doc["ip"],
            "mac": dev_doc.get("mac", "Unknown"),
            "hostname": dev_doc.get("hostname", "Unknown Host"),
            "friendly_name": dev_doc.get("friendly_name") or dev_doc.get("hostname") or f"Device ({dev_doc['ip']})",
            "device_type": dev_doc.get("device_type", "laptop" if "192.168" in dev_doc["ip"] else "phone"),
            "vendor": dev_doc.get("vendor", "Apple Inc." if "iPhone" in dev_doc.get("hostname", "") or "MacBook" in dev_doc.get("hostname", "") else "Network Device"),
            "first_seen": dev_doc.get("first_seen", log_time).isoformat(),
            "last_seen": dev_doc.get("last_seen", log_time).isoformat(),
            "is_online": True,
            "is_blocked": dev_doc.get("is_blocked", False),
            "total_queries": dev_doc.get("total_queries", 1),
            "notes": dev_doc.get("notes", "")
        }
        await ws_manager.broadcast_device_update(log.network_id, dev_payload)
    
    # If threat, log alert
    if is_threat:
        alert_id = str(uuid.uuid4())
        alert_doc = {
            "alert_id": alert_id,
            "network_id": log.network_id,
            "timestamp": log_time,
            "domain": clean_domain,
            "client_ip": log.client_ip,
            "client_name": client_name,
            "threat_type": threat_type,
            "severity": severity or "medium",
            "details": f"Query flagged as {threat_type} under category {category}",
            "is_resolved": False
        }
        await db.threat_alerts.insert_one(alert_doc)
        # Broadcast alert via websocket
        await ws_manager.broadcast_threat_alert(log.network_id, alert_doc)
        
    # Broadcast live log via websocket
    await ws_manager.broadcast_dns_log(log.network_id, {
        "id": log_id,
        "timestamp": log_time.isoformat(),
        "network_id": log.network_id,
        "gateway_id": log_doc["gateway_id"],
        "client_ip": log.client_ip,
        "client_mac": log_doc["client_mac"],
        "client_name": client_name,
        "domain": clean_domain,
        "category": category,
        "query_type": log_doc["query_type"],
        "response_code": log_doc["response_code"],
        "response_ips": log_doc["response_ips"],
        "response_time_ms": log_doc["response_time_ms"],
        "action": action,
        "is_threat": is_threat,
        "threat_type": threat_type,
        "threat_severity": severity
    })
    return log_doc

@router.post("/ingest")
async def ingest_single_log(
    log: DNSQueryIngest,
    authorized: bool = Depends(verify_gateway_api_key)
):
    db = await get_database()
    saved = await process_and_save_query(db, log)
    return {"status": "success", "log_id": saved["log_id"], "is_threat": saved["is_threat"]}

@router.post("/batch")
async def ingest_batch_logs(
    batch: DNSLogBatchIngest,
    authorized: bool = Depends(verify_gateway_api_key)
):
    db = await get_database()
    count = 0
    threat_count = 0
    for log_item in batch.logs:
        log_item.network_id = batch.network_id
        log_item.gateway_id = batch.gateway_id
        saved = await process_and_save_query(db, log_item)
        count += 1
        if saved.get("is_threat"):
            threat_count += 1
            
    return {"status": "success", "processed_count": count, "threats_detected": threat_count}

@router.get("", response_model=List[DNSLogResponse])
async def get_logs(
    network_id: Optional[str] = None,
    domain: Optional[str] = None,
    client_ip: Optional[str] = None,
    category: Optional[str] = None,
    is_threat: Optional[bool] = None,
    query_type: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = Query(default=100, le=1000),
    offset: int = 0,
    user: dict = Depends(get_current_user_optional)
):
    db = await get_database()
    filter_q = {}
    
    if network_id and network_id != "all":
        filter_q["network_id"] = network_id
    if domain:
        filter_q["domain"] = {"$regex": re.escape(domain), "$options": "i"}
    if client_ip:
        filter_q["client_ip"] = client_ip
    if category and category != "all":
        filter_q["category"] = category
    if is_threat is not None:
        filter_q["is_threat"] = is_threat
    if query_type:
        filter_q["query_type"] = query_type
        
    date_filter = {}
    if start_date:
        try:
            date_filter["$gte"] = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
        except Exception:
            pass
    if end_date:
        try:
            date_filter["$lte"] = datetime.fromisoformat(end_date.replace("Z", "+00:00"))
        except Exception:
            pass
            
    if date_filter:
        filter_q["timestamp"] = date_filter
        
    cursor = db.dns_logs.find(filter_q).sort("timestamp", -1).skip(offset).limit(limit)
    logs = await cursor.to_list(length=limit)
    
    results = []
    for l in logs:
        results.append(DNSLogResponse(
            id=l.get("log_id", str(l.get("_id", ""))),
            timestamp=l.get("timestamp", datetime.utcnow()),
            network_id=l.get("network_id", "default"),
            gateway_id=l.get("gateway_id", "gw_default"),
            client_ip=l.get("client_ip", "0.0.0.0"),
            client_mac=l.get("client_mac", "Unknown"),
            client_name=l.get("client_name") or l.get("client_ip", "Device"),
            domain=l.get("domain", ""),
            category=l.get("category", "General"),
            query_type=l.get("query_type", "A"),
            response_code=l.get("response_code", "NOERROR"),
            response_ips=l.get("response_ips", []),
            response_time_ms=float(l.get("response_time_ms", 0.0)),
            action=l.get("action", "FORWARDED"),
            is_threat=l.get("is_threat", False),
            threat_type=l.get("threat_type"),
            threat_severity=l.get("threat_severity")
        ))
    return results

@router.post("/cleanup")
async def cleanup_retention_logs(
    retention_days: int = Query(default=settings.DATA_RETENTION_DAYS),
    user: dict = Depends(get_current_user_optional)
):
    db = await get_database()
    cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
    del_res = await db.dns_logs.delete_many({"timestamp": {"$lt": cutoff_date}})
    return {
        "status": "success",
        "deleted_logs_count": del_res.deleted_count,
        "cutoff_date": cutoff_date.isoformat(),
        "retention_days": retention_days
    }
