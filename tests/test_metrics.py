from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200

def test_metrics_empty():
    response = client.get("/stores/STORE_1/metrics")
    assert response.status_code == 200
