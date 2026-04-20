# CHOICES.md

## 1. Detection Model Selection: YOLOv8
**Options Considered:** YOLOv8, YOLOv9, RT-DETR, MediaPipe.

**Decision:** YOLOv8 (specifically `yolov8n` for the default container).

**Rationale:**
The primary requirement for a retail store intelligence system is real-time performance on commodity hardware (often CPU-only or with modest GPUs). YOLOv8 provides the best balance between mean Average Precision (mAP) and inference speed. We chose the "nano" version to ensure that the `docker compose up` experience is smooth even on machines without dedicated NVIDIA hardware.
- **AI Suggestion:** Initially, an LLM suggested YOLOv9 for its state-of-the-art accuracy. However, I overrode this decision because the increased computational overhead would make the "Live Dashboard" bonus task much harder to achieve on standard laptops.
- **Edge Case Handling:** YOLOv8 handles partial occlusions and group entries remarkably well when paired with a robust tracker like DeepSORT.

## 2. Event Schema Design: Flat vs. Nested
**Options Considered:** Complex nested JSON (Store -> Visit -> Event) vs. Flat Event Stream.

**Decision:** Flat Event Schema.

**Rationale:**
For high-frequency event ingestion (like the `ZONE_DWELL` events emitted every 30s), a flat schema is superior for several reasons:
1. **Idempotency:** It is much easier to implement idempotent ingestion using a flat `event_id` primary key in a relational database.
2. **Query Performance:** SQL queries for metrics like "average dwell per zone" are significantly faster and simpler on flat tables compared to parsing nested JSON blobs or traversing deep hierarchies.
3. **Interoperability:** A flat schema is easier to emit into standard event brokers (like Kafka or RabbitMQ) should the system scale to 40+ stores.
- **AI Suggestion:** The AI suggested a nested schema for "semantic clarity," but I chose a flat one for operational robustness and simpler database normalization.

## 3. API Architecture: FastAPI Monolith
**Options Considered:** Microservices (Go/Node) vs. Monolith (FastAPI).

**Decision:** FastAPI Monolith.

**Rationale:**
Given the 48-hour window and the requirement for a "production-aware" but "containerized" solution, a FastAPI monolith provides the most efficient development-to-deployment ratio.
1. **Pydantic Validation:** Automatic schema validation for the `/events/ingest` endpoint ensures data integrity with minimal boilerplate.
2. **Asynchronous I/O:** FastAPI handles concurrent ingest batches (up to 500 events) efficiently, which is critical for real-time analytics.
3. **Portability:** Keeping the logic in a single service simplifies the `docker-compose.yml` and reduces the "moving parts" for the on-call engineer mentioned in the challenge.
- **One Choice Decision:** We chose SQLite as the storage engine because it is self-contained. While Postgres was considered, the overhead of managing a second container for a "take-home" scale project didn't justify the setup complexity.

## 4. Tracking Algorithm: DeepSORT
**Decision:** DeepSORT (Distance-based + Appearance features).

**Rationale:**
Standard YOLO tracking (BotSORT) is fast but can lose IDs during occlusions. DeepSORT uses appearance features which help maintain `visitor_id` consistency when customers move behind displays or cross paths, which is crucial for accurate unique visitor counts and funnel analysis.
