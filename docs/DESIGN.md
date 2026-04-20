# DESIGN.md - Store Intelligence Architecture

## Overview
The Apex Retail Store Intelligence system is an end-to-end pipeline designed to transform raw CCTV footage into actionable business metrics. The system is divided into two primary layers: the **Computer Vision Pipeline** and the **Intelligence API**.

## 1. Computer Vision Pipeline (The "Sensor")
The pipeline operates by processing frames from multiple camera angles (Entry, Floor, Billing). 
- **Detection (YOLOv8):** Each frame is passed through a YOLOv8n model to identify 'person' objects. We chose the nano model to ensure real-time capability (15fps) on standard hardware.
- **Tracking (DeepSORT):** Assigns a persistent `visitor_id`. It handles re-identification by maintaining track history.
- **Event Engine:** A custom state machine that monitors the coordinates and maps them to zones.
  - **REENTRY Detection:** The engine maintains a `recent_exits` cache. If a `visitor_id` is re-assigned to a track appearing at an entry point within 5 minutes of a prior `EXIT`, it emits a `REENTRY` event instead of a new `ENTRY`, preventing session inflation.
  - **Staff Identification:** A heuristic-based approach flags `is_staff: true` for individuals dwelling in non-billing zones for >10 minutes or exhibiting specific traversal patterns.

## 2. Intelligence API (The "Brain")
Built with FastAPI, this layer provides a production-ready surface for querying store health.
- **Ingestion:** A high-throughput endpoint that accepts batches of events. Idempotency is guaranteed by `event_id` primary key checks.
- **North Star Metrics:** 
  - **Conversion Rate:** Correlates `BILLING_ZONE` events with `pos_transactions.csv` using a 5-minute temporal window. This is the core business metric.
  - **Purchase Funnel:** A 4-stage funnel (Entry -> Zone Visit -> Billing Queue -> Purchase) that uses POS correlation to identify where customers drop off.
- **Production Hardening:**
  - **Structured Logging:** Middleware captures `trace_id`, `latency_ms`, and `status_code` for every request, formatted for ELK/Splunk ingestion.
  - **Graceful Degradation:** A global exception handler catches database failures and returns `503 Service Unavailable`, preventing stack trace leakage.
  - **Health Monitoring:** The `/health` endpoint detects `STALE_FEED` conditions if event ingestion lags by more than 10 minutes.

## AI-Assisted Decisions

1. **Schema Design (Prompted Gemini 1.5 Pro):** 
   - *Prompt:* "Design a robust JSON schema for a retail store tracking system that handles zones, dwell times, and staff detection. The schema must be flat for SQL indexing."
   - *Result:* The AI suggested the `session_seq` ordinal position to track visitor flow. I added a top-level `is_staff` field to ensure efficient indexing and exclusion in analytics queries.
2. **Re-entry Logic (Prompted Claude 3.5 Sonnet):**
   - *Prompt:* "What's the best way to handle customer re-entry in a retail CV system to avoid overcounting unique visitors?"
   - *Decision:* Adopted a "grace-period cache" strategy where exited visitor IDs are held for 300s. If a track with the same ID (or similar appearance vector) appears, it's flagged as `REENTRY`.
3. **Queue depth heuristic:** 
   - *Decision:* Calculated as `Joins - Abandons - Purchases`. This provides a real-time estimate of current queue pressure without requiring a separate "people in queue" counter.

## Trade-offs & Future Improvements
- **Privacy:** We strictly use anonymized `visitor_id` tokens. No facial data or biometrics are stored.
- **Scalability:** The system uses SQLite for simplicity in this challenge, but the architecture is ready for PostgreSQL.
- **VLM Integration:** Future versions could use a Vision-Language Model to classify staff uniforms or detect "billing queue frustration" through posture analysis.
