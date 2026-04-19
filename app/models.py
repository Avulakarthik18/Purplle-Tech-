from sqlalchemy import Column, String, Integer, Float
from .database import Base

class Event(Base):
    __tablename__ = "events"

    event_id = Column(String, primary_key=True, index=True)
    visitor_id = Column(String)
    event_type = Column(String)
    zone_id = Column(String)
    timestamp = Column(String)
    dwell_ms = Column(Integer)
    confidence = Column(Float)
