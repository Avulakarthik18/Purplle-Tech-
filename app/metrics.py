from fastapi import APIRouter
from .database import SessionLocal
from .models import Event
from .pos_loader import load_pos_data
import pandas as pd

router = APIRouter()

@router.get("/stores/{store_id}/metrics")
def get_metrics(store_id: str):
    db = SessionLocal()
    pos_df = load_pos_data()

    # Query customer events (strictly excluding staff)
    # Using 0/False explicitly for SQLite compatibility
    customer_events = db.query(Event).filter(Event.store_id == store_id, Event.is_staff == 0).all()

    visitors = {e.visitor_id for e in customer_events}
    billing_visitors = {} # visitor_id -> list of timestamps
    zone_dwells = {} 
    
    queue_joins = 0
    queue_abandons = 0

    for e in customer_events:
        # 1. Billing Interaction Logic
        if e.zone_id in ["CHECKOUT", "BILLING"]:
            ts = pd.to_datetime(e.timestamp, utc=True)
            billing_visitors.setdefault(e.visitor_id, []).append(ts)
        
        # 2. Dwell Logic
        if e.dwell_ms > 0:
            zone_dwells.setdefault(e.zone_id, []).append(e.dwell_ms)
        
        # 3. Queue Logic
        if e.event_type == "BILLING_QUEUE_JOIN":
            queue_joins += 1
        elif e.event_type == "BILLING_QUEUE_ABANDON":
            queue_abandons += 1

    # Match with POS for conversion (North Star Metric)
    converted = set()
    for _, txn in pos_df.iterrows():
        txn_time = pd.to_datetime(txn["timestamp"], utc=True)
        for visitor_id, times in billing_visitors.items():
            for t in times:
                diff = (txn_time - t).total_seconds()
                if 0 <= diff <= 300: # 5 min window
                    converted.add(visitor_id)
                    break # visitor converted by this txn

    total_visitors = len(visitors)
    conversion_rate = len(converted) / total_visitors if total_visitors else 0
    abandonment_rate = queue_abandons / queue_joins if queue_joins else 0
    
    avg_dwell_per_zone = {
        zone: round(sum(dwells) / len(dwells) / 1000, 2) if dwells else 0
        for zone, dwells in zone_dwells.items()
    }

    db.close()

    return {
        "store_id": store_id,
        "total_unique_visitors": total_visitors,
        "converted_visitors": len(converted),
        "conversion_rate": round(conversion_rate, 4),
        "abandonment_rate": round(abandonment_rate, 4),
        "avg_dwell_per_zone_sec": avg_dwell_per_zone,
        "current_queue_depth": max(0, queue_joins - queue_abandons - len(converted))
    }
