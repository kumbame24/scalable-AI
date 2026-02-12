from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class EventBase(BaseModel):
    source: str = Field(..., description="Source module (audio, video, etc)")
    session_id: int = Field(..., description="Exam session ID")
    sensor_id: int = Field(..., description="Sensor/camera ID")
    event_type: str = Field(..., description="Type of detected event")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score 0-1")
    timestamp: Optional[float] = Field(None, description="Unix timestamp of event")


class EventCreate(EventBase):
    pass


class Event(EventBase):
    event_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class AlertResponse(BaseModel):
    event_id: int
    source: str
    event_type: str
    confidence: float
    timestamp: Optional[float]
    created_at: datetime

    class Config:
        from_attributes = True


class FusedEvent(BaseModel):
    session_id: int
    fused_confidence: float = Field(..., ge=0.0, le=1.0)
    video_confidence: Optional[float] = None
    audio_confidence: Optional[float] = None
    combined_event_types: list[str]
    timestamp: float


class SessionStats(BaseModel):
    session_id: int
    total_events: int
    high_confidence_events: int
    event_types: dict[str, int]
    average_confidence: float

# Auth Schemas
class UserBase(BaseModel):
    username: str
    email: str
    role: str = "invigilator"

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# Examination Schemas
class ExaminationBase(BaseModel):
    title: str
    course_code: str
    duration_minutes: int

class ExaminationCreate(ExaminationBase):
    pass

class Examination(ExaminationBase):
    id: int
    start_time: datetime
    is_active: int
    created_at: datetime

    class Config:
        from_attributes = True
