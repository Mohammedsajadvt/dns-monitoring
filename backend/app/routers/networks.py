import uuid
from datetime import datetime, timedelta
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from app.database import get_database
from app.models import NetworkCreate, NetworkUpdate, NetworkResponse
from app.auth import get_current_user_optional

router = APIRouter(prefix="/api/networks", tags=["Networks"])

from app.network_detector import detect_current_wifi_network

@router.get("", response_model=List[NetworkResponse])
async def list_networks(user: dict = Depends(get_current_user_optional)):
    db = await get_database()
    cursor = db.networks.find().sort("created_at", -1)
    networks = await cursor.to_list(length=100)
    
    wifi_info = detect_current_wifi_network()

    if not networks:
        default_net = {
            "network_id": "net_default_primary",
            "name": wifi_info["name"],
            "location": wifi_info["location"],
            "description": f"Auto-detected active wireless gateway ({wifi_info['subnet']})",
            "subnet": wifi_info["subnet"],
            "created_at": datetime.utcnow()
        }
        await db.networks.insert_one(default_net)
        networks = [default_net]
    else:
        # If network has generic placeholder name, dynamically upgrade it to detected Wi-Fi SSID
        for net in networks:
            if net.get("name") in ["Primary Home / Office Wi-Fi", "Primary Wi-Fi Network", "Unnamed Network"]:
                await db.networks.update_one(
                    {"network_id": net["network_id"]},
                    {"$set": {
                        "name": wifi_info["name"],
                        "location": wifi_info["location"],
                        "subnet": wifi_info["subnet"]
                    }}
                )
                net["name"] = wifi_info["name"]
                net["location"] = wifi_info["location"]
                net["subnet"] = wifi_info["subnet"]
    
    result = []
    threshold_5m = datetime.utcnow() - timedelta(minutes=5)
    
    for net in networks:
        net_id = net["network_id"]
        # Count devices
        dev_count = await db.devices.count_documents({"network_id": net_id})
        # Check active gateway status
        gw = await db.gateways.find_one({"network_id": net_id})
        gw_online = False
        if gw and gw.get("last_heartbeat") and gw["last_heartbeat"] > threshold_5m:
            gw_online = True
            
        # Get last query log time
        last_log = await db.dns_logs.find_one({"network_id": net_id}, sort=[("timestamp", -1)])
        last_active = last_log["timestamp"] if last_log else None
        
        result.append(NetworkResponse(
            network_id=net_id,
            name=net.get("name", "Unnamed Network"),
            location=net.get("location", "Home/Office"),
            description=net.get("description", ""),
            subnet=net.get("subnet", "192.168.1.0/24"),
            created_at=net.get("created_at", datetime.utcnow()),
            device_count=dev_count,
            gateway_online=gw_online,
            last_active=last_active
        ))
    return result

@router.post("", response_model=NetworkResponse)
async def create_network(payload: NetworkCreate, user: dict = Depends(get_current_user_optional)):
    db = await get_database()
    net_id = f"net_{uuid.uuid4().hex[:8]}"
    new_doc = {
        "network_id": net_id,
        "name": payload.name,
        "location": payload.location or "Location",
        "description": payload.description or "",
        "subnet": payload.subnet or "192.168.1.0/24",
        "created_at": datetime.utcnow()
    }
    await db.networks.insert_one(new_doc)
    return NetworkResponse(
        network_id=net_id,
        name=new_doc["name"],
        location=new_doc["location"],
        description=new_doc["description"],
        subnet=new_doc["subnet"],
        created_at=new_doc["created_at"],
        device_count=0,
        gateway_online=False,
        last_active=None
    )

@router.put("/{network_id}", response_model=NetworkResponse)
async def update_network(network_id: str, payload: NetworkUpdate, user: dict = Depends(get_current_user_optional)):
    db = await get_database()
    update_data = {k: v for k, v in payload.dict().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")
        
    res = await db.networks.update_one({"network_id": network_id}, {"$set": update_data})
    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="Network not found")
        
    net = await db.networks.find_one({"network_id": network_id})
    dev_count = await db.devices.count_documents({"network_id": network_id})
    return NetworkResponse(
        network_id=net["network_id"],
        name=net["name"],
        location=net.get("location", ""),
        description=net.get("description", ""),
        subnet=net.get("subnet", ""),
        created_at=net.get("created_at", datetime.utcnow()),
        device_count=dev_count,
        gateway_online=False,
        last_active=None
    )

@router.delete("/{network_id}")
async def delete_network(network_id: str, user: dict = Depends(get_current_user_optional)):
    db = await get_database()
    await db.networks.delete_one({"network_id": network_id})
    await db.devices.delete_many({"network_id": network_id})
    await db.dns_logs.delete_many({"network_id": network_id})
    await db.threat_alerts.delete_many({"network_id": network_id})
    await db.gateways.delete_many({"network_id": network_id})
    return {"status": "success", "message": f"Network {network_id} and associated records deleted"}

@router.post("/auto-detect", response_model=NetworkResponse)
async def auto_detect_network(user: dict = Depends(get_current_user_optional)):
    db = await get_database()
    wifi_info = detect_current_wifi_network()
    
    # Check if a network already exists for user
    existing_net = await db.networks.find_one()
    if existing_net:
        net_id = existing_net["network_id"]
        await db.networks.update_one(
            {"network_id": net_id},
            {"$set": {
                "name": wifi_info["name"],
                "location": wifi_info["location"],
                "subnet": wifi_info["subnet"],
                "description": f"Auto-detected active wireless gateway ({wifi_info['subnet']})"
            }}
        )
    else:
        net_id = f"net_{uuid.uuid4().hex[:8]}"
        new_doc = {
            "network_id": net_id,
            "name": wifi_info["name"],
            "location": wifi_info["location"],
            "description": f"Auto-detected active wireless gateway ({wifi_info['subnet']})",
            "subnet": wifi_info["subnet"],
            "created_at": datetime.utcnow()
        }
        await db.networks.insert_one(new_doc)
        
    net = await db.networks.find_one({"network_id": net_id})
    dev_count = await db.devices.count_documents({"network_id": net_id})
    return NetworkResponse(
        network_id=net["network_id"],
        name=net["name"],
        location=net.get("location", ""),
        description=net.get("description", ""),
        subnet=net.get("subnet", ""),
        created_at=net.get("created_at", datetime.utcnow()),
        device_count=dev_count,
        gateway_online=True,
        last_active=datetime.utcnow()
    )

