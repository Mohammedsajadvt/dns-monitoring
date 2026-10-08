import uuid
from datetime import datetime, timedelta
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from app.database import get_database
from app.models import GatewayRegister, GatewayHeartbeat, GatewayResponse
from app.auth import generate_gateway_api_key, get_current_user_optional

router = APIRouter(prefix="/api/gateways", tags=["Gateways"])

@router.get("", response_model=List[GatewayResponse])
async def list_gateways(network_id: str = None, user: dict = Depends(get_current_user_optional)):
    db = await get_database()
    query = {"network_id": network_id} if network_id else {}
    cursor = db.gateways.find(query)
    gateways = await cursor.to_list(length=50)
    
    threshold_3m = datetime.utcnow() - timedelta(minutes=3)
    results = []
    for gw in gateways:
        is_online = bool(gw.get("last_heartbeat") and gw["last_heartbeat"] > threshold_3m)
        results.append(GatewayResponse(
            gateway_id=gw["gateway_id"],
            network_id=gw["network_id"],
            gateway_name=gw.get("gateway_name", "DNS Gateway"),
            gateway_type=gw.get("gateway_type", "linux_pc"),
            ip_address=gw.get("ip_address", "127.0.0.1"),
            api_key=gw.get("api_key", ""),
            is_online=is_online,
            last_heartbeat=gw.get("last_heartbeat"),
            version=gw.get("version", "1.0.0")
        ))
    return results

@router.post("/register", response_model=GatewayResponse)
async def register_gateway(payload: GatewayRegister):
    db = await get_database()
    # Check if network exists
    net = await db.networks.find_one({"network_id": payload.network_id})
    if not net:
        # Create network if does not exist
        await db.networks.insert_one({
            "network_id": payload.network_id,
            "name": f"Network ({payload.network_id})",
            "location": "Gateway Location",
            "description": "Auto-registered from gateway agent",
            "subnet": "192.168.1.0/24",
            "created_at": datetime.utcnow()
        })
        
    gateway_id = f"gw_{uuid.uuid4().hex[:8]}"
    api_key = generate_gateway_api_key(payload.network_id)
    
    doc = {
        "gateway_id": gateway_id,
        "network_id": payload.network_id,
        "gateway_name": payload.gateway_name,
        "gateway_type": payload.gateway_type,
        "ip_address": payload.ip_address or "127.0.0.1",
        "api_key": api_key,
        "version": payload.version or "1.0.0",
        "registered_at": datetime.utcnow(),
        "last_heartbeat": datetime.utcnow()
    }
    await db.gateways.insert_one(doc)
    
    return GatewayResponse(
        gateway_id=gateway_id,
        network_id=payload.network_id,
        gateway_name=payload.gateway_name,
        gateway_type=payload.gateway_type,
        ip_address=doc["ip_address"],
        api_key=api_key,
        is_online=True,
        last_heartbeat=doc["last_heartbeat"],
        version=doc["version"]
    )

@router.post("/heartbeat")
async def gateway_heartbeat(payload: GatewayHeartbeat):
    db = await get_database()
    now = datetime.utcnow()
    
    await db.gateways.update_one(
        {"gateway_id": payload.gateway_id},
        {"$set": {
            "network_id": payload.network_id,
            "last_heartbeat": now,
            "cpu_usage": payload.cpu_usage,
            "memory_usage": payload.memory_usage,
            "active_devices": payload.active_devices,
            "uptime_seconds": payload.uptime_seconds
        }},
        upsert=True
    )
    return {"status": "ok", "server_time": now.isoformat()}
