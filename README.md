# Apex Retail: Store Intelligence System

An end-to-end computer vision and analytics pipeline for offline retail store intelligence.

## 🚀 Overview

This system transforms raw CCTV footage into a queryable Intelligence API. It identifies customers, tracks their movement across store zones, detects anomalies, and correlates behavior with POS transactions to compute conversion rates.

### Core Pipeline
1. **Detection:** YOLOv8n (optimized for 15fps inference).
2. **Tracking:** DeepSORT with appearance-based re-identification.
3. **Intelligence API:** FastAPI with SQLite for idempotent event ingestion.
4. **Dashboard:** Streamlit for real-time visualization of metrics and funnels.

## 🛠️ Quick Start

### 1. Prerequisite: Dataset
Place the raw challenge data in `data/dataset/`:
- `videos/`: Store CCTV clips (.mp4)
- `store_layout.json`: Zone definitions
- `pos_transactions.csv`: Transaction logs

### 2. Run the API (Production Mode)
The entire API layer, including the database and anomaly detection, is containerized.
```bash
docker compose up --build
```
API will be available at `http://localhost:8000`.

### 3. Run the Computer Vision Pipeline
This script processes the clips and generates behavior events.
```bash
# Install local dependencies
pip install -r requirements.txt

# Process all videos (saves to data/events.json)
python pipeline/track.py

# Feed events into the API
python pipeline/emit.py
```

### 4. View Dashboard
```bash
streamlit run dashboard.py
```

## 🧠 Edge Case Handling

- **Staff Exclusion:** The pipeline uses a dwell-time and multi-zone trajectory heuristic to flag `is_staff: true`. These events are automatically excluded from customer conversion and funnel metrics.
- **Re-entry:** DeepSORT maintains feature vectors for IDs; if a customer leaves and returns within the "max_age" window, they retain their `visitor_id`, preventing session inflation.
- **Idempotency:** Every event has a UUID. `POST /events/ingest` uses SQL `UPSERT` logic to ensure that re-processing a clip never double-counts data.
- **Occlusions:** Confidence thresholds degrade gracefully; tracks are maintained for 30 frames of total occlusion before being finalized.

## 📊 API Surface

| Endpoint | Description | Key Metric |
| :--- | :--- | :--- |
| `GET /metrics` | Store performance | Conversion Rate, Avg Dwell, Queue Depth |
| `GET /funnel` | Drop-off analysis | Entry -> Zone -> Billing -> Purchase |
| `GET /heatmap` | Traffic density | Frequency vs. Dwell normalized 0-100 |
| `GET /anomalies` | Operational alerts | Queue Spikes, Conversion Drops |
| `GET /health` | System status | Stale feed warnings, DB connectivity |

**Local Access:**
- Dashboard: [http://localhost:9501](http://localhost:9501)
- API Docs: [http://localhost:9000/docs](http://localhost:9000/docs)

## 🧪 Testing
Run the test suite with coverage reporting:
```bash
pytest --cov=app tests/
```
*Note: All test files include mandatory AI prompt blocks documenting their generation.*
