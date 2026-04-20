# Apex Retail: Store Intelligence System

An end-to-end computer vision and intelligence pipeline for transforming raw CCTV footage into actionable retail analytics.

## 🚀 Overview

This system turns a data "blind spot" (offline stores) into a real-time intelligence surface. It identifies customers, tracks movement across zones, detects operational anomalies, and correlates behavior with POS data to compute the **North Star Metric: Conversion Rate**.

### Key Technologies
- **Vision:** YOLOv8n + DeepSORT (15fps optimized).
- **Backend:** FastAPI (Async) + SQLite (Persistent).
- **UI:** Streamlit + Plotly (Real-time).
- **Infra:** Docker Compose (Multi-container architecture).

---

## 🛠️ Quick Start (Production)

The entire system is containerized. No manual setup is required beyond cloning and running Docker.

### 1. Prerequisites
Ensure you have the challenge dataset in the following structure:
- `data/dataset/videos/`: (.mp4 clips)
- `data/dataset/store_layout.json`: Zone metadata
- `data/dataset/pos_transactions.csv`: Sales logs

### 2. Launch Everything
```bash
docker compose up --build -d
```
This command automatically starts:
1.  **Intelligence API** (`:9001`)
2.  **Analytics Dashboard** (`:9002`)
3.  **CV Processor** (Background script that processes video clips automatically)

### 3. Access Surfaces
- **Interactive Dashboard:** [http://localhost:9002](http://localhost:9002)
- **API Documentation:** [http://localhost:9001/docs](http://localhost:9001/docs)
- **Health Check:** [http://localhost:9001/health](http://localhost:9001/health)

---

## 🧠 Solved Retail Edge Cases

- **Staff Exclusion:** Uses a dwell-time and multi-zone trajectory heuristic to flag `is_staff: true`. Staff are automatically excluded from conversion metrics.
- **Re-entry Logic:** The `EventEngine` maintains a "grace-period cache" (300s) to identify physical re-entry, preventing session inflation.
- **POS Correlation:** Matches `BILLING_ZONE` events with `pos_transactions.csv` timestamps (5-minute window) to track conversions without a `customer_id`.
- **Anomaly Prescriptions:** Detects `DEAD_ZONE`, `QUEUE_SPIKES`, and `CONVERSION_DROPS` with prescriptive `suggested_action` strings.
- **Production Hardening:** Structured logging (Trace IDs), Idempotent ingestion, and 503 Graceful Degradation for DB failures.

---

## 📊 Analytics Endpoints

| Endpoint | North Star Metric | Description |
| :--- | :--- | :--- |
| `GET /metrics` | **Conversion Rate** | Unique visitors, conversion, queue depth. |
| `GET /funnel` | **Drop-off %** | Entry -> Zone Visit -> Billing Queue -> Purchase. |
| `GET /heatmap` | **Traffic Density** | Normalized zone visit frequency vs dwell. |
| `GET /anomalies` | **Operational Risks** | Active alerts with suggested manager actions. |
| `GET /health` | **System Latency** | `STALE_FEED` warning if data lag > 10 min. |

---

## 🧪 Testing
The system includes 11 comprehensive tests verifying idempotency, staff exclusion, and API stability.
```bash
docker exec -e PYTHONPATH=. store-intelligence-api python -m pytest tests/
```

---

## 📂 Documentation for Reviewers
- **[DESIGN.md](docs/DESIGN.md)**: Architecture overview and "AI-Assisted Decisions" log.
- **[CHOICES.md](docs/CHOICES.md)**: Rationale for YOLOv8, Flat Schema, and FastAPI.
- **Tests**: Every test file contains mandatory `# PROMPT:` and `# CHANGES MADE:` headers.
