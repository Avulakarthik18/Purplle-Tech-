from sqlalchemy import Column, String, Integer, Float, JSON, Boolean
from .database import Base

class Event(Base):
    __tablename__ = "events"

    event_id = Column(String, primary_key=True, index=True)
    store_id = Column(String)
    camera_id = Column(String)
    visitor_id = Column(String)
    event_type = Column(String)
    zone_id = Column(String)
    timestamp = Column(String)
    dwell_ms = Column(Integer)
    is_staff = Column(Boolean, default=False)
    confidence = Column(Float)
    event_metadata = Column(JSON)
