# CHOICES.md - Architectural Decisions

This document details three critical architectural decisions made during the development of the Store Intelligence system.

## 1. Detection Model: YOLOv8 Nano
**Options Considered:** YOLOv8 (Nano vs Small), RT-DETR, MediaPipe
**AI Suggestion:** Gemini suggested YOLOv8s for better accuracy on occluded individuals.
**My Choice:** YOLOv8n (Nano)
**Rationale:** In a retail CCTV environment, inference speed is critical. Most CCTV cameras run at 15fps. YOLOv8n provides ~25-30fps on a standard CPU, allowing for overhead in the tracking and event generation stages. While 'Small' is more accurate, 'Nano' is sufficient for person detection in well-lit store environments and ensures the "Live Dashboard" remains responsive without high-end GPU requirements.

## 2. Event Schema: Flat vs Nested
**Options Considered:** 
- Nested: `{ visitor: { id: 1, type: "staff" }, event: { ... } }`
- Flat: `{ visitor_id: 1, is_staff: true, ... }`
**AI Suggestion:** Claude suggested a nested JSONB structure for flexibility in future metadata.
**My Choice:** Flat Schema with top-level `is_staff` and `store_id`.
**Rationale:** For an Intelligence API that computes metrics on-the-fly, query performance is paramount. A flat schema allows for direct indexing on `visitor_id`, `store_id`, and `is_staff`. This makes the `GET /metrics` query (which excludes staff) significantly faster as it avoids complex JSON path traversals during the aggregation phase.

## 3. API Architecture: FastAPI with SQLite
**Options Considered:** Flask, FastAPI, Node.js/Express
**AI Suggestion:** FastAPI was recommended for its native async support and automatic OpenAPI documentation.
**My Choice:** FastAPI with SQLite
**Rationale:** FastAPI's Pydantic validation ensures that malformed events from the pipeline are caught before they reach the database. SQLite was chosen over PostgreSQL for this specific challenge to meet the "No manual steps beyond git clone" requirement. By using SQLAlchemy, the system remains database-agnostic, allowing for a seamless transition to a production RDS/PostgreSQL instance in the future.

## 4. Anomaly Detection Strategy
**My Choice:** Threshold-based logic with descriptive `suggested_action`.
**Rationale:** While ML-based anomaly detection (e.g., Isolation Forests) is powerful, it requires a "burn-in" period of historical data. For a new store deployment, threshold-based logic (e.g., "Queue > 5 people") provides immediate value. We added `suggested_action` strings to transform raw data into "Prescriptive Analytics," which is more valuable for store managers.
