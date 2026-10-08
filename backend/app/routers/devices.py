from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from app.database import get_database
from app.models import DeviceResponse, DeviceUpdate
from app.auth import get_current_user_optional

router = APIRouter(prefix="/api/devices", tags=["Devices"])

@router.get("", response_model=List[DeviceResponse])
async def list_devices(
    network_id: Optional[str] = None,
    user: dict = Depends(get_current_user_optional)
):
    db = await get_database()
    filter_q = {}
    if network_id and network_id != "all":
        filter_q["network_id"] = network_id
        
    cursor = db.devices.find(filter_q).sort("last_seen", -1)
    devices = await cursor.to_list(length=200)
    
    threshold_10m = datetime.utcnow() - timedelta(minutes=10)
    results = []
    
    for dev in devices:
        last_seen = dev.get("last_seen", datetime.utcnow())
        is_online = bool(last_seen > threshold_10m)
        
        results.append(DeviceResponse(
            network_id=dev["network_id"],
            ip=dev["ip"],
            mac=dev.get("mac", "Unknown"),
            hostname=dev.get("hostname", "Unknown Host"),
            friendly_name=dev.get("friendly_name") or dev.get("hostname") or f"Device ({dev['ip']})",
            device_type=dev.get("device_type", "unknown"),
            vendor=dev.get("vendor", "Unknown Vendor"),
            first_seen=dev.get("first_seen", datetime.utcnow()),
            last_seen=last_seen,
            is_online=is_online,
            is_blocked=dev.get("is_blocked", False),
            total_queries=dev.get("total_queries", 0),
            notes=dev.get("notes", "")
        ))
    return results

@router.put("/{network_id}/{ip}", response_model=DeviceResponse)
async def update_device(
    network_id: str,
    ip: str,
    payload: DeviceUpdate,
    user: dict = Depends(get_current_user_optional)
):
    db = await get_database()
    update_data = {k: v for k, v in payload.dict().items() if v is not None}
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields provided for update")
        
    res = await db.devices.update_one(
        {"network_id": network_id, "ip": ip},
        {"$set": update_data}
    )
    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="Device not found")
        
    dev = await db.devices.find_one({"network_id": network_id, "ip": ip})
    resp = DeviceResponse(
        network_id=dev["network_id"],
        ip=dev["ip"],
        mac=dev.get("mac", "Unknown"),
        hostname=dev.get("hostname", "Unknown Host"),
        friendly_name=dev.get("friendly_name") or dev.get("hostname") or f"Device ({dev['ip']})",
        device_type=dev.get("device_type", "unknown"),
        vendor=dev.get("vendor", "Unknown Vendor"),
        first_seen=dev.get("first_seen", datetime.utcnow()),
        last_seen=dev.get("last_seen", datetime.utcnow()),
        is_online=True,
        is_blocked=dev.get("is_blocked", False),
        total_queries=dev.get("total_queries", 0),
        notes=dev.get("notes", "")
    )
    from app.websocket_manager import ws_manager
    await ws_manager.broadcast_device_update(network_id, resp.dict())
    return resp
