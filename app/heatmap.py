from fastapi import APIRouter
from .database import SessionLocal
from .models import Event
from collections import Counter

router = APIRouter()

@router.get("/stores/{store_id}/heatmap")
def get_heatmap(store_id: str):
    db = SessionLocal()
    
    # Query events (excluding staff)
    events = db.query(Event).filter(Event.store_id == store_id).all()
    customer_events = [e for e in events if not (e.event_metadata or {}).get("is_staff", False)]
    
    visitors = {e.visitor_id for e in customer_events}
    
    # Frequency: Count visits (ZONE_ENTER events)
    zone_visits = Counter([e.zone_id for e in customer_events if e.event_type == "ZONE_ENTER"])
    
    # Average Dwell
    zone_dwells = {}
    for e in customer_events:
        if e.dwell_ms > 0:
            zone_dwells.setdefault(e.zone_id, []).append(e.dwell_ms)
    
    avg_dwells = {
        zone: sum(dwells) / len(dwells) 
        for zone, dwells in zone_dwells.items()
    }
    
    # Normalization (0-100)
    max_visits = max(zone_visits.values()) if zone_visits else 1
    max_dwell = max(avg_dwells.values()) if avg_dwells else 1
    
    heatmap_data = {}
    all_zones = set(zone_visits.keys()) | set(avg_dwells.keys())
    
    for zone in all_zones:
        freq_score = (zone_visits.get(zone, 0) / max_visits) * 100
        dwell_score = (avg_dwells.get(zone, 0) / max_dwell) * 100
        
        heatmap_data[zone] = {
            "frequency_score": round(freq_score, 2),
            "dwell_score": round(dwell_score, 2),
            "combined_score": round((freq_score + dwell_score) / 2, 2)
        }
    
    db.close()
    
    return {
        "store_id": store_id,
        "data_confidence": len(visitors) >= 20,
        "session_count": len(visitors),
        "heatmap": heatmap_data
    }
