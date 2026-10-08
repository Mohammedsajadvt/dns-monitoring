import io
import csv
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Query, Response
from app.database import get_database
from app.auth import get_current_user_optional

router = APIRouter(prefix="/api/export", tags=["Export & Audit"])

@router.get("/csv")
async def export_dns_logs_csv(
    network_id: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = Query(default=5000, le=50000),
    user: dict = Depends(get_current_user_optional)
):
    db = await get_database()
    filter_q = {}
    if network_id and network_id != "all":
        filter_q["network_id"] = network_id
        
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
        
    cursor = db.dns_logs.find(filter_q).sort("timestamp", -1).limit(limit)
    logs = await cursor.to_list(length=limit)
    
    # Audit log entry
    await db.audit_logs.insert_one({
        "event": "CSV_EXPORT",
        "user": user.get("email") if user else "anonymous",
        "timestamp": datetime.utcnow(),
        "record_count": len(logs),
        "network_id": network_id or "all"
    })
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Timestamp (UTC)",
        "Network ID",
        "Client IP",
        "Client Name",
        "Client MAC",
        "Domain Queried",
        "Category",
        "Query Type",
        "Response Code",
        "Response Time (ms)",
        "Action",
        "Is Threat",
        "Threat Type"
    ])
    
    for l in logs:
        writer.writerow([
            l.get("timestamp", "").isoformat() if isinstance(l.get("timestamp"), datetime) else str(l.get("timestamp")),
            l.get("network_id", ""),
            l.get("client_ip", ""),
            l.get("client_name", ""),
            l.get("client_mac", ""),
            l.get("domain", ""),
            l.get("category", ""),
            l.get("query_type", ""),
            l.get("response_code", ""),
            l.get("response_time_ms", 0.0),
            l.get("action", ""),
            l.get("is_threat", False),
            l.get("threat_type", "")
        ])
        
    csv_data = output.getvalue()
    filename = f"dns_history_export_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
    
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.get("/audit")
async def get_audit_logs(
    limit: int = 50,
    user: dict = Depends(get_current_user_optional)
):
    db = await get_database()
    cursor = db.audit_logs.find().sort("timestamp", -1).limit(limit)
    logs = await cursor.to_list(length=limit)
    for l in logs:
        l["id"] = str(l.get("_id", ""))
        l.pop("_id", None)
    return logs
