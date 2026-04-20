from fastapi import APIRouter
from datetime import datetime, timezone
from app.database import SessionLocal
from app.models import Event
from sqlalchemy import func
import pandas as pd

router = APIRouter()

@router.get("/health")
def health():
    db = SessionLocal()
    try:
        # Get unique store IDs
        stores = db.query(Event.store_id).distinct().all()
        active_stores = [s[0] for s in stores if s[0]]
        
        # Get last event timestamp
        last_event_str = db.query(func.max(Event.timestamp)).scalar()
        
        status = "healthy"
        warnings = []
        
        if last_event_str:
            last_event_ts = pd.to_datetime(last_event_str, utc=True)
            now = datetime.now(timezone.utc)
            lag_minutes = (now - last_event_ts).total_seconds() / 60
            
            if lag_minutes > 10:
                status = "degraded"
                warnings.append({
                    "code": "STALE_FEED",
                    "message": f"Last event was received {round(lag_minutes, 1)} minutes ago. Threshold is 10 min.",
                    "lag_minutes": round(lag_minutes, 1)
                })
        
        return {
            "status": status,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "active_stores": active_stores,
            "last_event_timestamp": last_event_str,
            "warnings": warnings if warnings else None
        }
    finally:
        db.close()
