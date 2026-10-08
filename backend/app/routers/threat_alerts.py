import uuid
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from app.database import get_database
from app.models import ThreatAlertResponse, BlockedDomainCreate
from app.auth import get_current_user_optional

router = APIRouter(prefix="/api/threats", tags=["Threat Alerts & Blocklist"])

@router.get("/alerts", response_model=List[ThreatAlertResponse])
async def list_threat_alerts(
    network_id: Optional[str] = None,
    resolved: Optional[bool] = None,
    limit: int = 100,
    user: dict = Depends(get_current_user_optional)
):
    db = await get_database()
    filter_q = {}
    if network_id and network_id != "all":
        filter_q["network_id"] = network_id
    if resolved is not None:
        filter_q["is_resolved"] = resolved
        
    cursor = db.threat_alerts.find(filter_q).sort("timestamp", -1).limit(limit)
    alerts = await cursor.to_list(length=limit)
    
    return [
        ThreatAlertResponse(
            id=a.get("alert_id", str(a.get("_id"))),
            network_id=a["network_id"],
            timestamp=a.get("timestamp", datetime.utcnow()),
            domain=a.get("domain", ""),
            client_ip=a.get("client_ip", "0.0.0.0"),
            client_name=a.get("client_name", "Device"),
            threat_type=a.get("threat_type", "Suspicious Activity"),
            severity=a.get("severity", "medium"),
            details=a.get("details", "Threat flag triggered"),
            is_resolved=a.get("is_resolved", False)
        )
        for a in alerts
    ]

@router.post("/alerts/{alert_id}/resolve")
async def resolve_alert(alert_id: str, user: dict = Depends(get_current_user_optional)):
    db = await get_database()
    res = await db.threat_alerts.update_one(
        {"alert_id": alert_id},
        {"$set": {"is_resolved": True, "resolved_at": datetime.utcnow()}}
    )
    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    from app.websocket_manager import ws_manager
    alert = await db.threat_alerts.find_one({"alert_id": alert_id})
    if alert:
        await ws_manager.broadcast_threat_alert(alert["network_id"], {
            "id": alert_id,
            "is_resolved": True,
            "domain": alert.get("domain", ""),
            "threat_type": alert.get("threat_type", "")
        })
    return {"status": "success", "message": "Alert marked as resolved"}

@router.get("/blocklist")
async def get_blocklist(
    network_id: Optional[str] = None,
    user: dict = Depends(get_current_user_optional)
):
    db = await get_database()
    filter_q = {"network_id": network_id} if network_id else {}
    cursor = db.blocked_domains.find(filter_q).sort("added_at", -1)
    items = await cursor.to_list(length=500)
    for it in items:
        it["id"] = str(it.get("_id", ""))
        it.pop("_id", None)
    return items

@router.post("/blocklist")
async def add_to_blocklist(
    payload: BlockedDomainCreate,
    user: dict = Depends(get_current_user_optional)
):
    db = await get_database()
    clean_domain = payload.domain.lower().strip().rstrip(".")
    
    doc = {
        "network_id": payload.network_id,
        "domain": clean_domain,
        "category": payload.category,
        "reason": payload.reason,
        "added_at": datetime.utcnow()
    }
    await db.blocked_domains.update_one(
        {"network_id": payload.network_id, "domain": clean_domain},
        {"$set": doc},
        upsert=True
    )
    return {"status": "success", "message": f"Domain {clean_domain} added to network blocklist"}

@router.delete("/blocklist/{network_id}/{domain}")
async def remove_from_blocklist(
    network_id: str,
    domain: str,
    user: dict = Depends(get_current_user_optional)
):
    db = await get_database()
    clean_domain = domain.lower().strip()
    res = await db.blocked_domains.delete_one({"network_id": network_id, "domain": clean_domain})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Domain not found in blocklist")
    return {"status": "success", "message": f"Domain {clean_domain} removed from blocklist"}
