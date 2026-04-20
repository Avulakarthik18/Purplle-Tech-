# PROMPT: "Generate a pytest file to validate the Event schema for the Store Intelligence API. Test for the new top-level is_staff field and ensured metadata is correctly mapped."
# CHANGES MADE: Added integration tests with the FastAPI client to verify actual database mapping.

import pytest
from fastapi.testclient import TestClient
from app.main import app
import uuid

client = TestClient(app)

def test_event_schema_staff_top_level():
    """Verify that is_staff is correctly handled at the top level and reflected in metrics."""
    event_id = str(uuid.uuid4())
    test_store = f"STORE_STAFF_{uuid.uuid4().hex[:6]}"
    payload = [{
        "event_id": event_id,
        "store_id": test_store,
        "camera_id": "CAM_01",
        "visitor_id": "VIS_STAFF_001",
        "event_type": "ZONE_ENTER",
        "is_staff": True, # Top level
        "timestamp": "2026-04-20T12:00:00Z",
        "metadata": {"role": "manager"}
    }]
    
    # Ingest
    response = client.post("/events/ingest", json=payload)
    assert response.status_code == 200
    
    # Verify metrics excludes this visitor
    metrics_resp = client.get(f"/stores/{test_store}/metrics")
    assert metrics_resp.status_code == 200
    data = metrics_resp.json()
    assert data["total_unique_visitors"] == 0 # Staff should be excluded

def test_event_schema_customer():
    """Verify that a standard customer event is included in metrics."""
    event_id = str(uuid.uuid4())
    payload = [{
        "event_id": event_id,
        "store_id": "STORE_SCHEMA_TEST",
        "camera_id": "CAM_01",
        "visitor_id": "VIS_CUST_001",
        "event_type": "ENTRY",
        "is_staff": False,
        "timestamp": "2026-04-20T12:05:00Z"
    }]
    
    # Ingest
    client.post("/events/ingest", json=payload)
    
    # Verify metrics includes this visitor
    metrics_resp = client.get("/stores/STORE_SCHEMA_TEST/metrics")
    data = metrics_resp.json()
    assert data["total_unique_visitors"] >= 1
