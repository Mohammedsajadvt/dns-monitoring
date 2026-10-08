from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, Depends, Query
from app.database import get_database
from app.models import QuickStats
from app.auth import get_current_user_optional

router = APIRouter(prefix="/api/analytics", tags=["Analytics & Statistics"])

@router.get("/summary", response_model=QuickStats)
async def get_analytics_summary(
    network_id: Optional[str] = None,
    user: dict = Depends(get_current_user_optional)
):
    db = await get_database()
    match_q: Dict[str, Any] = {}
    if network_id and network_id != "all":
        match_q["network_id"] = network_id
        
    now = datetime.utcnow()
    start_of_day = datetime(now.year, now.month, now.day)
    
    # 1. Total queries today
    today_match = {**match_q, "timestamp": {"$gte": start_of_day}}
    total_queries_today = await db.dns_logs.count_documents(today_match)
    
    # 2. Active devices in last 24h
    threshold_24h = now - timedelta(hours=24)
    dev_match = {"last_seen": {"$gte": threshold_24h}}
    if network_id and network_id != "all":
        dev_match["network_id"] = network_id
    active_devices_count = await db.devices.count_documents(dev_match)
    if active_devices_count == 0:
        active_devices_count = await db.devices.count_documents({"network_id": network_id} if network_id and network_id != "all" else {})
    if active_devices_count == 0:
        distinct_ips = await db.dns_logs.distinct("client_ip", match_q)
        active_devices_count = len(distinct_ips)
    
    # 3. Threats blocked today
    threat_match = {**today_match, "is_threat": True}
    threats_blocked_today = await db.dns_logs.count_documents(threat_match)
    
    # 4. Top domains aggregation
    top_domains_pipeline = [
        {"$match": match_q},
        {"$group": {"_id": "$domain", "count": {"$sum": 1}, "category": {"$first": "$category"}}},
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ]
    top_domains_cursor = db.dns_logs.aggregate(top_domains_pipeline)
    top_domains_raw = await top_domains_cursor.to_list(length=10)
    top_domains = [{"domain": d["_id"], "count": d["count"], "category": d.get("category", "General")} for d in top_domains_raw]
    
    # 5. Hourly query timeline (last 24 hours)
    timeline_pipeline = [
        {"$match": {**match_q, "timestamp": {"$gte": threshold_24h}}},
        {
            "$group": {
                "_id": {
                    "year": {"$year": "$timestamp"},
                    "month": {"$month": "$timestamp"},
                    "day": {"$dayOfMonth": "$timestamp"},
                    "hour": {"$hour": "$timestamp"}
                },
                "total": {"$sum": 1},
                "threats": {"$sum": {"$cond": [{"$eq": ["$is_threat", True]}, 1, 0]}}
            }
        },
        {"$sort": {"_id.year": 1, "_id.month": 1, "_id.day": 1, "_id.hour": 1}}
    ]
    timeline_cursor = db.dns_logs.aggregate(timeline_pipeline)
    timeline_raw = await timeline_cursor.to_list(length=24)
    
    query_timeline = []
    for item in timeline_raw:
        hour_val = item["_id"]["hour"]
        query_timeline.append({
            "hour": f"{hour_val:02d}:00",
            "total": item["total"],
            "threats": item["threats"]
        })
        
    # 6. Category distribution
    cat_pipeline = [
        {"$match": match_q},
        {"$group": {"_id": "$category", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    cat_cursor = db.dns_logs.aggregate(cat_pipeline)
    cat_raw = await cat_cursor.to_list(length=15)
    category_distribution = [{"category": c["_id"] or "Uncategorized", "count": c["count"]} for c in cat_raw]
    
    # 7. Threat breakdown
    threat_pipeline = [
        {"$match": {**match_q, "is_threat": True}},
        {"$group": {"_id": "$threat_type", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    threat_cursor = db.dns_logs.aggregate(threat_pipeline)
    threat_raw = await threat_cursor.to_list(length=10)
    threat_breakdown = [{"threat_type": t["_id"] or "Unknown Threat", "count": t["count"]} for t in threat_raw]
    
    return QuickStats(
        total_queries_today=total_queries_today,
        active_devices_count=active_devices_count,
        threats_blocked_today=threats_blocked_today,
        top_domains=top_domains,
        query_timeline=query_timeline,
        category_distribution=category_distribution,
        threat_breakdown=threat_breakdown
    )
