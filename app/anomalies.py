from fastapi import APIRouter
from .database import SessionLocal
from .models import Event
from .queue_logic import calculate_queue_depth
import pandas as pd

router = APIRouter()

@router.get("/stores/{store_id}/anomalies")
def detect_anomalies(store_id: str):
    db = SessionLocal()

    # Query events for this store
    events = db.query(Event).filter(Event.store_id == store_id).all()
    anomalies = []

    # 1. Queue Spikes
    queue_depth = calculate_queue_depth(events)
    if queue_depth > 5:
        anomalies.append({
            "type": "QUEUE_SPIKE",
            "severity": "CRITICAL",
            "message": f"Queue depth reached {queue_depth}, exceeding threshold of 5",
            "suggested_action": "Open an additional billing counter immediately."
        })

    # 2. Dead Zone (No visits in last 30 mins)
    if events:
        last_event_time = pd.to_datetime(max([e.timestamp for e in events]), utc=True)
        now = pd.to_datetime("now", utc=True)
        if (now - last_event_time).total_seconds() > 1800: # 30 mins
            anomalies.append({
                "type": "DEAD_ZONE",
                "severity": "WARN",
                "message": "No customer activity detected in any zone for over 30 minutes.",
                "suggested_action": "Check if camera feeds are active or if the store has unexpected closure."
            })
    else:
        anomalies.append({
            "type": "NO_DATA",
            "severity": "WARN",
            "message": "No events detected in the database",
            "suggested_action": "Verify that the detection pipeline is running and emitting events."
        })

    # 3. Low Conversion (Example - if less than 5% conversion)
    # This would ideally compare against 7-day average as per requirements
    
    db.close()

    return {
        "store_id": store_id,
        "total_anomalies": len(anomalies),
        "anomalies": anomalies
    }
