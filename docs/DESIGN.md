# DESIGN.md

## Architecture

Pipeline:
Video → Detection → Tracking → Events → API → Metrics

## Components

- **YOLOv8**: Person detection (Fast and Accurate)
- **DeepSORT**: Multi-object tracking
- **FastAPI**: Backend REST API
- **SQLite**: Local relational storage for events and metrics

## AI-Assisted Decisions

1. **Model Choice**: Compared YOLO vs other models; chose YOLO for speed and edge deployment compatibility.
2. **Schema Design**: Used AI for event schema design; modified for simplicity to reduce database overhead.
3. **Storage**: AI suggested Redis, but chose SQLite for simplicity and persistence without external dependencies.

## Trade-offs

- **Accuracy vs Speed**: Chose speed (YOLOv8n) to ensure real-time processing on standard hardware.
- **Complexity vs Maintainability**: Started with simple zones and a flat schema instead of an exact layout to ensure robustness.
