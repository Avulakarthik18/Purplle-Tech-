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
                exists = db.query(Event).filter(Event.event_id == e["event_id"]).first()
                if exists:
                    continue  # idempotent

                # Filter out fields not in the model if any
                model_data = {k: v for k, v in e.items() if k in Event.__table__.columns.keys()}
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
        return {"error": str(e)}
    finally:
        db.close()
