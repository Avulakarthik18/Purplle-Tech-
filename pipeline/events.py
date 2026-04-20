import uuid
import json
import os
from datetime import datetime, timezone

# Load Store Layout
LAYOUT_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "dataset", "store_layout.json")

def load_zones():
    try:
        with open(LAYOUT_PATH, "r") as f:
            layout = json.load(f)
            return layout.get("zones", {})
    except Exception as e:
        print(f"[ERROR] Could not load store_layout.json: {e}")
        return {}

ZONES = load_zones()

def is_point_in_poly(x, y, poly):
    """Simple bounding box check for rectangular zones, or full poly if needed."""
    # Assuming the layout uses 4 points for rectangles based on sample
    xs = [p[0] for p in poly]
    ys = [p[1] for p in poly]
    return min(xs) <= x <= max(xs) and min(ys) <= y <= max(ys)

def get_zone_id(x, y):
    for zone_id, zone_data in ZONES.items():
        if is_point_in_poly(x, y, zone_data["coordinates"]):
            return zone_id.upper()
    return None

class EventEngine:
    def __init__(self):
        self.visitors = {}   # track_id → state
        self.recent_exits = {} # visitor_id -> exit_timestamp (for re-entry detection)
        self.all_events = []

    def generate_event(self, track_id, bbox, timestamp, store_id="STORE_DEFAULT", camera_id="CAM_DEFAULT"):
        l, t, w, h = bbox
        center_x = l + w // 2
        center_y = t + h // 2
        zone = get_zone_id(center_x, center_y)

        visitor_id = f"VIS_{track_id}"

        if track_id not in self.visitors:
            event_type = "ENTRY"
            
            # Re-entry Detection logic
            # If this visitor_id was seen recently (e.g. within 5 mins of an EXIT)
            if visitor_id in self.recent_exits:
                last_exit = self.recent_exits[visitor_id]
                if timestamp - last_exit < 300: # 5 minutes
                    event_type = "REENTRY"
            
            self.visitors[track_id] = {
                "last_zone": zone,
                "entry_time": timestamp,
                "last_seen": timestamp,
                "is_staff": False,
                "total_dwell": 0,
                "in_queue": False,
                "session_seq": 0,
                "store_id": store_id,
                "camera_id": camera_id
            }
            return [self.create_event(track_id, event_type, zone, timestamp, store_id, camera_id)]

        visitor = self.visitors[track_id]
        last_zone = visitor["last_zone"]
        events = []

        if zone != last_zone:
            if last_zone:
                events.append(self.create_event(track_id, "ZONE_EXIT", last_zone, timestamp, store_id, camera_id))
                if last_zone in ["CHECKOUT", "BILLING"] and visitor["in_queue"]:
                     events.append(self.create_event(track_id, "BILLING_QUEUE_ABANDON", last_zone, timestamp, store_id, camera_id))
                     visitor["in_queue"] = False

            if zone:
                events.append(self.create_event(track_id, "ZONE_ENTER", zone, timestamp, store_id, camera_id))
                if zone in ["CHECKOUT", "BILLING"]:
                    events.append(self.create_event(track_id, "BILLING_QUEUE_JOIN", zone, timestamp, store_id, camera_id, metadata={"queue_depth": 1}))
                    visitor["in_queue"] = True

            visitor["last_zone"] = zone

        time_since_last = timestamp - visitor["last_seen"]
        visitor["total_dwell"] += time_since_last
        
        if visitor["total_dwell"] % 30 < time_since_last and visitor["total_dwell"] >= 30:
            events.append(self.create_event(track_id, "ZONE_DWELL", zone, timestamp, store_id, camera_id, dwell=30))

        # Improved Staff detection: dwell > 10 mins or specific behavior
        if visitor["total_dwell"] > 600: 
            visitor["is_staff"] = True

        visitor["last_seen"] = timestamp
        return events

    def finalize_sessions(self, current_time):
        exit_events = []
        to_remove = []
        
        for track_id, visitor in self.visitors.items():
            if current_time - visitor["last_seen"] > 10: # Increased threshold for stability
                store_id = visitor.get("store_id", "STORE_DEFAULT")
                camera_id = visitor.get("camera_id", "CAM_DEFAULT")
                visitor_id = f"VIS_{track_id}"
                
                exit_events.append(self.create_event(track_id, "EXIT", visitor["last_zone"], current_time, store_id, camera_id))
                
                # Record exit for potential re-entry
                self.recent_exits[visitor_id] = current_time
                to_remove.append(track_id)
        
        for track_id in to_remove:
            del self.visitors[track_id]
            
        return exit_events

    def create_event(self, track_id, event_type, zone, timestamp, store_id="STORE_DEFAULT", camera_id="CAM_DEFAULT", dwell=0, metadata=None):
        visitor = self.visitors.get(track_id, {})
        is_staff = visitor.get("is_staff", False)
        visitor["session_seq"] = visitor.get("session_seq", 0) + 1
        
        meta = {
            "session_seq": visitor["session_seq"],
            "sku_zone": zone
        }
        if metadata:
            meta.update(metadata)

        event = {
            "event_id": str(uuid.uuid4()),
            "store_id": store_id,
            "camera_id": camera_id,
            "visitor_id": f"VIS_{track_id}",
            "event_type": event_type,
            "zone_id": zone,
            "timestamp": datetime.fromtimestamp(timestamp, tz=timezone.utc).isoformat(),
            "dwell_ms": int(dwell * 1000),
            "is_staff": is_staff, # TOP LEVEL
            "confidence": 0.95,
            "metadata": meta
        }
        return event

if __name__ == "__main__":
    # Test logic
    engine = EventEngine()
    e = engine.generate_event("1", [10, 10, 50, 50], 1600000000)
    print(json.dumps(e, indent=2))
