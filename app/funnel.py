from fastapi import APIRouter
from .database import SessionLocal
from .models import Event
from .pos_loader import load_pos_data
import pandas as pd

router = APIRouter()

@router.get("/stores/{store_id}/funnel")
def get_funnel(store_id: str):
    db = SessionLocal()
    pos_df = load_pos_data()
    
    # Query events (excluding staff)
    events = db.query(Event).filter(Event.store_id == store_id, Event.is_staff == False).all()

    entry = set()
    zone = set()
    billing = set()
    billing_visitors = {} # visitor_id -> list of timestamps in billing zone

    for e in events:
        if e.event_type == "ENTRY":
            entry.add(e.visitor_id)

        if e.event_type == "ZONE_ENTER":
            zone.add(e.visitor_id)

        if e.zone_id in ["BILLING", "CHECKOUT"]:
            billing.add(e.visitor_id)
            ts = pd.to_datetime(e.timestamp, utc=True)
            billing_visitors.setdefault(e.visitor_id, []).append(ts)

    # 4. Purchase Logic (Correlation with POS)
    purchased = set()
    for _, txn in pos_df.iterrows():
        txn_time = pd.to_datetime(txn["timestamp"], utc=True)
        for visitor_id, times in billing_visitors.items():
            for t in times:
                diff = (txn_time - t).total_seconds()
                if 0 <= diff <= 300: # 5 min window
                    purchased.add(visitor_id)
                    break

    db.close()

    return {
        "store_id": store_id,
        "entry": len(entry),
        "zone_visit": len(zone),
        "billing_queue": len(billing),
        "purchase": len(purchased),
        "conversion": {
            "entry_to_zone_pct": round(len(zone)/len(entry)*100, 2) if entry else 0,
            "zone_to_billing_pct": round(len(billing)/len(zone)*100, 2) if zone else 0,
            "billing_to_purchase_pct": round(len(purchased)/len(billing)*100, 2) if billing else 0,
            "overall_conversion_pct": round(len(purchased)/len(entry)*100, 2) if entry else 0
        }
    }
