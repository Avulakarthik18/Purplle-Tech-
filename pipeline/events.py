import uuid
import json
import os
from datetime import datetime, timezone

# Zone Definitions
ZONES = {
    "ENTRY": [(0, 0), (300, 300)],
    "FLOOR": [(300, 0), (900, 800)],
    "BILLING": [(900, 0), (1280, 800)]
}

def get_zone(x, y):
    for zone, ((x1, y1), (x2, y2)) in ZONES.items():
        if x1 <= x <= x2 and y1 <= y <= y2:
            return zone
    return "UNKNOWN" # Default zone if not matched

class EventEngine:
    def __init__(self):
        self.visitors = {}   # track_id → state
        self.all_events = []

    def generate_event(self, track_id, bbox, timestamp):
        # Handle bbox format [l, t, w, h] from deep-sort
        l, t, w, h = bbox
        center_x = l + w // 2
        center_y = t + h // 2

        zone = get_zone(center_x, center_y)

        if track_id not in self.visitors:
            self.visitors[track_id] = {
                "last_zone": zone,
                "entry_time": timestamp,
                "last_seen": timestamp,
                "is_staff": False,
                "total_dwell": 0
            }
            return self.create_event(track_id, "ENTRY", zone, timestamp)

        visitor = self.visitors[track_id]
        last_zone = visitor["last_zone"]
        events = []

        # Zone change logic
        if zone != last_zone:
            if last_zone:
                events.append(self.create_event(track_id, "ZONE_EXIT", last_zone, timestamp))
            if zone:
                events.append(self.create_event(track_id, "ZONE_ENTER", zone, timestamp))
            visitor["last_zone"] = zone

        # Dwell logic (simplified check)
        time_diff = timestamp - visitor["last_seen"]
        visitor["total_dwell"] += time_diff
        
        # Staff filter (Step 8)
        if visitor["total_dwell"] > 300: # 5 minutes
            visitor["is_staff"] = True

        visitor["last_seen"] = timestamp
        return events

    def finalize_sessions(self, current_time):
        """Detect exits for visitors not seen for more than 5 seconds."""
        exit_events = []
        to_remove = []
        
        for track_id, visitor in self.visitors.items():
            if current_time - visitor["last_seen"] > 5:
                exit_events.append(self.create_event(track_id, "EXIT", visitor["last_zone"], current_time))
                to_remove.append(track_id)
        
        for track_id in to_remove:
            del self.visitors[track_id]
            
        return exit_events

    def create_event(self, track_id, event_type, zone, timestamp, dwell=0):
        # Handle Staff meta
        is_staff = self.visitors.get(track_id, {}).get("is_staff", False)
        
        event = {
            "event_id": str(uuid.uuid4()),
            "visitor_id": f"VIS_{track_id}",
            "event_type": event_type,
            "zone_id": zone,
            "timestamp": datetime.fromtimestamp(timestamp, tz=timezone.utc).isoformat(),
            "dwell_ms": int(dwell * 1000),
            "confidence": 0.9,
            "metadata": {
                "is_staff": is_staff
            }
        }
        return event

if __name__ == "__main__":
    # Test logic
    engine = EventEngine()
    e = engine.generate_event("1", [10, 10, 50, 50], 1600000000)
    print(json.dumps(e, indent=2))
