/*Exams Table*/
CREATE TABLE exams (
    exam_id SERIAL PRIMARY KEY,
    exam_name VARCHAR(100) NOT NULL,
    exam_date TIMESTAMP NOT NULL,
    duration_minutes INT NOT NULL,
    location VARCHAR(100)
);

/*Candidates Table*/
CREATE TABLE candidates (
    candidate_id SERIAL PRIMARY KEY,
    exam_id INT REFERENCES exams(exam_id),
    anonymous_code VARCHAR(20) UNIQUE NOT NULL
);

/*Exam Sessions*/
CREATE TABLE exam_sessions (
    session_id SERIAL PRIMARY KEY,
    exam_id INT REFERENCES exams(exam_id),
    candidate_id INT REFERENCES candidates(candidate_id),
    start_time TIMESTAMP,
    end_time TIMESTAMP
);

/*Sensors Table*/
CREATE TABLE sensors (
    sensor_id SERIAL PRIMARY KEY,
    sensor_type VARCHAR(20) CHECK (sensor_type IN ('video', 'audio')),
    location VARCHAR(50)
);

/*Events Table*/
CREATE TABLE events (
    event_id SERIAL PRIMARY KEY,
    session_id INT REFERENCES exam_sessions(session_id),
    sensor_id INT REFERENCES sensors(sensor_id),
    event_type VARCHAR(50),
    confidence FLOAT CHECK (confidence BETWEEN 0 AND 1),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

/*Event Evidence*/
CREATE TABLE event_evidence (
    evidence_id SERIAL PRIMARY KEY,
    event_id INT REFERENCES events(event_id),
    evidence_type VARCHAR(20), -- frame, clip, metadata
    evidence_path TEXT
);

/*Fused Alerts Table*/
CREATE TABLE fused_alerts (
    alert_id SERIAL PRIMARY KEY,
    session_id INT REFERENCES exam_sessions(session_id),
    video_event_id INT REFERENCES events(event_id),
    audio_event_id INT REFERENCES events(event_id),
    fused_confidence FLOAT CHECK (fused_confidence BETWEEN 0 AND 1),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

/*Human Decisions Table*/
CREATE TABLE human_decisions (
    decision_id SERIAL PRIMARY KEY,
    alert_id INT REFERENCES fused_alerts(alert_id),
    reviewer_role VARCHAR(30), -- invigilator, supervisor
    decision VARCHAR(20) CHECK (decision IN ('ignore', 'monitor', 'flag')),
    comments TEXT,
    decided_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

/*System Logs*/
CREATE TABLE system_logs (
    log_id SERIAL PRIMARY KEY,
    module VARCHAR(30),
    message TEXT,
    log_level VARCHAR(10),
    logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

/*PERFORMANCE & AUDIT INDEXES*/
CREATE INDEX idx_events_session ON events(session_id);
CREATE INDEX idx_events_time ON events(created_at);
CREATE INDEX idx_alerts_session ON fused_alerts(session_id);
