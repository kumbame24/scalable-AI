from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

# Adjust imports to match package structure
from backend.database.database import SessionLocal, engine, get_db
from backend.database import models
from backend.schemas import (
    EventCreate, Event, AlertResponse, SessionStats, 
    UserCreate, User as UserSchema, Token,
    ExaminationCreate, Examination as ExaminationSchema
)
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from backend.auth_utils import get_password_hash, verify_password, create_access_token, verify_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    username = verify_token(token)
    if username is None:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    user = db.query(models.User).filter(models.User.username == username).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Scalable AI Backend",
    version="1.0.0",
    description="Backend API for exam monitoring system"
)

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {
        "status": "online",
        "service": "Scalable AI Backend",
        "version": "1.0.0"
    }

# Authentication Endpoints
@app.post("/auth/register", response_model=UserSchema)
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # Single Admin Constraint
    if user.role.lower() == "admin":
        admin_exists = db.query(models.User).filter(models.User.role == "admin").first()
        if admin_exists:
            raise HTTPException(status_code=400, detail="An Admin already exists in the system")
    
    hashed_password = get_password_hash(user.password)
    new_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        role=user.role.lower()
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/auth/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=UserSchema)
def read_users_me(current_user: models.User = Depends(get_current_user)):
    return current_user

@app.post("/events", response_model=dict)
def receive_event(event: EventCreate, db: Session = Depends(get_db)):
    """
    Receive an event from AI modules and store it.
    Validates using Pydantic schema.
    """
    try:
        # If session_id is 1 (placeholder) or not provided, try to find the actual active exam
        effective_session_id = event.session_id
        if effective_session_id == 1 or not effective_session_id:
            active_exam = db.query(models.Examination).filter(models.Examination.is_active == 1).first()
            if active_exam:
                effective_session_id = active_exam.id

        # Create event record
        db_event = models.Event(
            source=event.source,
            session_id=effective_session_id,
            sensor_id=event.sensor_id,
            event_type=event.event_type,
            confidence=event.confidence,
            timestamp=event.timestamp
        )
        db.add(db_event)
        db.commit()
        db.refresh(db_event)
        
        logger.info(f"Event stored: {event.event_type} from {event.source} (conf: {event.confidence:.2f})")
        
        return {
            "status": "stored",
            "event_id": db_event.event_id,
            "timestamp": event.timestamp
        }
    except Exception as e:
        logger.error(f"Error storing event: {e}")
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error storing event: {str(e)}")

@app.get("/alerts", response_model=List[AlertResponse])
def get_alerts(
    confidence: float = Query(0.65, ge=0.0, le=1.0),
    limit: int = Query(100, ge=1, le=1000),
    session_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Retrieve high-confidence events filtered by confidence threshold.
    """
    try:
        query = db.query(models.Event).filter(models.Event.confidence > confidence)
        
        if session_id:
            query = query.filter(models.Event.session_id == session_id)
        
        events = query.order_by(models.Event.created_at.desc()).limit(limit).all()
        return events
    except Exception as e:
        logger.error(f"Error retrieving alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/session/{session_id}/stats", response_model=SessionStats)
def get_session_stats(session_id: int, db: Session = Depends(get_db)):
    """
    Get statistics for a specific exam session.
    """
    try:
        events = db.query(models.Event).filter(
            models.Event.session_id == session_id
        ).all()
        
        if not events:
            return SessionStats(
                session_id=session_id,
                total_events=0,
                high_confidence_events=0,
                event_types={},
                average_confidence=0.0
            )
        
        high_conf = len([e for e in events if e.confidence > 0.65])
        event_types = {}
        total_conf = 0
        
        for e in events:
            event_types[e.event_type] = event_types.get(e.event_type, 0) + 1
            total_conf += e.confidence
        
        return SessionStats(
            session_id=session_id,
            total_events=len(events),
            high_confidence_events=high_conf,
            event_types=event_types,
            average_confidence=total_conf / len(events) if events else 0.0
        )
    except Exception as e:
        logger.error(f"Error getting session stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "backend"}

# Examination Endpoints
@app.post("/examinations", response_model=ExaminationSchema)
def create_examination(
    exam: ExaminationCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only Chief Proctors can create examinations")
    
    db_exam = models.Examination(
        title=exam.title,
        course_code=exam.course_code,
        duration_minutes=exam.duration_minutes,
        is_active=1
    )
    db.add(db_exam)
    db.commit()
    db.refresh(db_exam)
    return db_exam

@app.get("/examinations", response_model=List[ExaminationSchema])
def list_examinations(db: Session = Depends(get_db)):
    return db.query(models.Examination).order_by(models.Examination.created_at.desc()).all()

@app.get("/examinations/active", response_model=Optional[ExaminationSchema])
def get_active_examination(db: Session = Depends(get_db)):
    return db.query(models.Examination).filter(models.Examination.is_active == 1).first()

@app.post("/examinations/{exam_id}/finalize")
def finalize_examination(
    exam_id: int, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.role != "admin" and current_user.role != "proctor":
        raise HTTPException(status_code=403, detail="Not authorized to finalize")
    
    db_exam = db.query(models.Examination).filter(models.Examination.id == exam_id).first()
    if not db_exam:
        raise HTTPException(status_code=404, detail="Examination not found")
    
    db_exam.is_active = 0
    db.commit()
    return {"status": "finalized", "exam_id": exam_id}

@app.get("/users/count")
def get_user_count(role: str = "student", db: Session = Depends(get_db)):
    """Return count of users by role."""
    count = db.query(models.User).filter(models.User.role == role).count()
    return {"count": count}

@app.get("/users", response_model=List[UserSchema])
def list_users(
    role: Optional[str] = None, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """List all users, optionally filtered by role. Admin/Proctor only."""
    if current_user.role not in ["admin", "proctor"]:
        raise HTTPException(status_code=403, detail="Not authorized to list users")
    
    query = db.query(models.User)
    if role:
        query = query.filter(models.User.role == role)
    
    return query.order_by(models.User.created_at.desc()).all()

import csv
import io
from fastapi.responses import StreamingResponse

@app.get("/session/{session_id}/export")
def export_session_events(session_id: int, db: Session = Depends(get_db)):
    """Export all events for a session as CSV."""
    events = db.query(models.Event).filter(models.Event.session_id == session_id).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Event ID", "Source", "Type", "Confidence", "Timestamp", "Created At"])
    
    for event in events:
        writer.writerow([
            event.event_id, 
            event.source, 
            event.event_type, 
            event.confidence, 
            event.timestamp, 
            event.created_at
        ])
    
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=session_{session_id}_report.csv"}
    )

