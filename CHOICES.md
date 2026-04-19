# CHOICES.md

## 1. Detection Model

**Options:**
- YOLOv8
- RT-DETR

**AI Suggestion:**
YOLOv8

**Final Choice:**
YOLOv8 because it's fast, has great community support, and is easy to integrate with tracking libraries.

---

## 2. Event Schema

**Options:**
- Complex nested schema
- Flat schema

**Choice:**
Flat schema for simplicity, ease of querying in SQLite, and lower serialization overhead.

---

## 3. API Architecture

**Options:**
- Microservices
- Monolith

**Choice:**
Monolith (FastAPI) for simplicity, speed of development, and easier deployment for this scale of project.
