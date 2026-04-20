from fastapi import APIRouter, Body, HTTPException
from .database import SessionLocal
from .models import Event
from .logger import logger

router = APIRouter()

@router.post("/events/ingest")
def ingest_events(events: list = Body(...)):
    db = SessionLocal()
    inserted = 0
    errors = []

    try:
        for e in events:
            try:
                # 1. Idempotency Check
                event_id = e.get("event_id")
                if not event_id:
                    errors.append("Missing event_id in payload")
                    continue

                exists = db.query(Event).filter(Event.event_id == event_id).first()
                if exists:
                    continue  # Idempotent: ignore if already exists

                # 2. Extract top-level fields
                model_data = {
                    "event_id": event_id,
                    "store_id": e.get("store_id"),
                    "camera_id": e.get("camera_id"),
                    "visitor_id": e.get("visitor_id"),
                    "event_type": e.get("event_type"),
                    "zone_id": e.get("zone_id"),
                    "timestamp": e.get("timestamp"),
                    "dwell_ms": e.get("dwell_ms", 0),
                    "is_staff": e.get("is_staff", False),
                    "confidence": e.get("confidence", 1.0),
                    "event_metadata": e.get("metadata", {})
                }
                
                # 3. Create and add
                event = Event(**model_data)
                db.add(event)
                inserted += 1
            except Exception as item_err:
                errors.append(f"Event {e.get('event_id', 'unknown')}: {str(item_err)}")

        db.commit()
        logger.info(f"Ingested {inserted} events successfully. Total errors: {len(errors)}")
        
        return {
            "status": "success",
            "inserted": inserted,
            "errors": errors if errors else None
        }
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to ingest events: {str(e)}")
        raise HTTPException(status_code=500, detail="Database ingestion error")
    finally:
        db.close()
