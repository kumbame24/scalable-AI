from sqlalchemy import Column, Integer, String, Float, ForeignKey, TIMESTAMP
from .database import Base
import datetime

class Event(Base):
    __tablename__ = "events"
    event_id = Column(Integer, primary_key=True)
    source = Column(String, default="unknown")
    session_id = Column(Integer)
    sensor_id = Column(Integer)
    event_type = Column(String)
    confidence = Column(Float)
    timestamp = Column(Float, nullable=True)
    created_at = Column(TIMESTAMP, default=datetime.datetime.utcnow)

    def to_dict(self):
        return {
            "event_id": self.event_id,
            "source": self.source,
            "session_id": self.session_id,
            "sensor_id": self.sensor_id,
            "event_type": self.event_type,
            "confidence": self.confidence,
            "timestamp": self.timestamp,
            "created_at": self.created_at
        }

    def __repr__(self):
        return f"<Event(id={self.event_id}, type={self.event_type}, conf={self.confidence}, source={self.source})>"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default="invigilator")
    is_active = Column(Integer, default=1)
    created_at = Column(TIMESTAMP, default=datetime.datetime.utcnow)

class Examination(Base):
    __tablename__ = "examinations"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    course_code = Column(String, index=True)
    start_time = Column(TIMESTAMP, default=datetime.datetime.utcnow)
    duration_minutes = Column(Integer)
    is_active = Column(Integer, default=1)
    created_at = Column(TIMESTAMP, default=datetime.datetime.utcnow)
