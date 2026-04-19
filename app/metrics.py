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

    events = db.query(Event).all()

    visitors = set()
    billing_visitors = {}

    for e in events:
        visitors.add(e.visitor_id)

        if e.zone_id == "BILLING":
            # Ensure timestamp is datetime and UTC-aware for comparison
            ts = pd.to_datetime(e.timestamp, utc=True)
            billing_visitors.setdefault(e.visitor_id, []).append(ts)

    converted = set()

    # Match with POS
    for _, txn in pos_df.iterrows():
        txn_time = pd.to_datetime(txn["timestamp"], utc=True)

        for visitor_id, times in billing_visitors.items():
            for t in times:
                # Converted if in billing zone within 5 minutes BEFORE a transaction
                diff = (txn_time - t).total_seconds()
                if 0 <= diff <= 300:
                    converted.add(visitor_id)

    total_visitors = len(visitors)
    conversion_rate = len(converted) / total_visitors if total_visitors else 0

    db.close()

    return {
        "total_visitors": total_visitors,
        "converted_visitors": len(converted),
        "conversion_rate": round(conversion_rate, 2),
        "store_id": store_id
    }
