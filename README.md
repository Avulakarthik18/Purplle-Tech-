# Store Intelligence System

Retail store intelligence pipeline using YOLOv8, DeepSORT, and FastAPI.

## 🚀 Setup

```bash
# Clone the repository
git clone <repo>
cd store-intelligence

# Run with Docker
docker compose up --build
```

📊 API Endpoints
- `POST /events/ingest`: Ingest detection events
- `GET /stores/{id}/metrics`: Get store performance metrics
- `GET /stores/{id}/funnel`: Get customer funnel analysis
- `GET /stores/{id}/anomalies`: Detect behavior anomalies
- `GET /health`: System health check

🎥 Run Detection Pipeline
```bash
python pipeline/track.py
```

📦 Dataset
Place dataset inside: `data/dataset/`
