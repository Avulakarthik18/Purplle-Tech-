from fastapi import APIRouter
from .database import SessionLocal
from .models import Event
from .queue_logic import calculate_queue_depth

router = APIRouter()

@router.get("/stores/{store_id}/anomalies")
def detect_anomalies(store_id: str):
    db = SessionLocal()

    events = db.query(Event).all()

    anomalies = []

    # 1. Queue Spikes
    queue_depth = calculate_queue_depth(events)
    if queue_depth > 5:
        anomalies.append({
            "type": "QUEUE_SPIKE",
            "severity": "CRITICAL",
            "message": f"Queue depth reached {queue_depth}, exceeding threshold of 5"
        })

    # 2. Data Health
    if len(events) == 0:
        anomalies.append({
            "type": "NO_DATA",
            "severity": "WARN",
            "message": "No events detected in the database"
        })

    # 3. Low Conversion Anomaly (example)
    # Could be added here by matching with POS data

    db.close()

    return {
        "store_id": store_id,
        "total_anomalies": len(anomalies),
        "anomalies": anomalies
    }
