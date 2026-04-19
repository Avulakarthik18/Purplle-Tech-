from fastapi import APIRouter
from .database import SessionLocal
from .models import Event

router = APIRouter()

@router.get("/stores/{store_id}/funnel")
def get_funnel(store_id: str):
    db = SessionLocal()
    events = db.query(Event).all()

    entry = set()
    zone = set()
    billing = set()

    for e in events:
        if e.event_type == "ENTRY":
            entry.add(e.visitor_id)

        if e.event_type == "ZONE_ENTER":
            zone.add(e.visitor_id)

        if e.zone_id == "BILLING":
            billing.add(e.visitor_id)

    db.close()

    # Drop-off calculations
    drop_off_zone = entry - zone
    drop_off_billing = zone - billing

    return {
        "store_id": store_id,
        "entry": len(entry),
        "zone_visit": len(zone),
        "billing": len(billing),
        "drop_off_zone_count": len(drop_off_zone),
        "drop_off_billing_count": len(drop_off_billing),
        "funnel_efficiency": {
            "entry_to_zone": round(len(zone)/len(entry), 2) if entry else 0,
            "zone_to_billing": round(len(billing)/len(zone), 2) if zone else 0
        }
    }
