import { useState, useEffect, useRef } from "react";
import { AlertTriangle, ShieldAlert, Zap, Info } from "lucide-react";

function ViolationCard({ violation }) {
    const getEventColor = (eventType) => {
        if (eventType?.includes("GAZE")) return "#EF4444"; // Red
        if (eventType?.includes("OBJECT")) return "#F59E0B"; // Amber
        if (eventType?.includes("AUDIO")) return "#10B981"; // Emerald
        return "#3B82F6"; // Blue
    };

    const getEventIcon = (eventType) => {
        if (eventType?.includes("GAZE")) return <AlertTriangle size={18} />;
        if (eventType?.includes("OBJECT")) return <ShieldAlert size={18} />;
        if (eventType?.includes("AUDIO")) return <Zap size={18} />;
        return <Info size={18} />;
    };

    const formatTime = (timestamp) => {
        if (!timestamp) return "N/A";
        // Handle both ISO string and Unix timestamp
        const date = isNaN(timestamp) ? new Date(timestamp) : new Date(timestamp * 1000);
        return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    };

    const confidenceLevel = violation?.confidence > 0.8 ? "high" : violation?.confidence > 0.65 ? "medium" : "low";

    return (
        <div
            className={`violation-card animate-slide-in ${confidenceLevel}`}
            style={{ borderLeft: `4px solid ${getEventColor(violation?.event_type)}` }}
        >
            <div className="violation-header">
                <div className="violation-type-group">
                    <span className="violation-icon" style={{ color: getEventColor(violation?.event_type) }}>
                        {getEventIcon(violation?.event_type)}
                    </span>
                    <span className="violation-type">{violation?.event_type?.replace(/_/g, ' ') || "UNKNOWN"}</span>
                </div>
                <span className={`confidence-badge conf-${confidenceLevel}`}>
                    {((violation?.confidence || 0) * 100).toFixed(0)}%
                </span>
            </div>
            <div className="violation-body">
                <span className="violation-time">{formatTime(violation?.timestamp)}</span>
                <span className="violation-source">Source: {violation?.source?.toUpperCase() || "AI"}</span>
            </div>
        </div>
    );
}

export default function ViolationFeed() {
    const [violations, setViolations] = useState([]);
    const [lastId, setLastId] = useState(null);
    const audioRef = useRef(null);

    // Alert sound (gentle notification)
    const playNotification = () => {
        try {
            const audio = new Audio("https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3");
            audio.volume = 0.4;
            audio.play();
        } catch (e) {
            console.warn("Audio playback failed:", e);
        }
    };

    useEffect(() => {
        const fetchViolations = async () => {
            try {
                // Fetch active exam first to filter by session
                const activeRes = await fetch("http://localhost:8000/examinations/active");
                let url = "http://localhost:8000/alerts?limit=15";

                if (activeRes.ok) {
                    const activeExam = await activeRes.json();
                    if (activeExam) {
                        url += `&session_id=${activeExam.id}`;
                    }
                }

                const res = await fetch(url);
                if (res.ok) {
                    const data = await res.json();

                    if (data.length > 0) {
                        const newestId = data[0].event_id;
                        if (lastId && newestId !== lastId) {
                            playNotification();
                        }
                        setLastId(newestId);
                    }

                    setViolations(data);
                }
            } catch (err) {
                console.error("Failed to fetch violations:", err);
            }
        };

        fetchViolations();
        const interval = setInterval(fetchViolations, 3000);
        return () => clearInterval(interval);
    }, [lastId]);

    return (
        <div className="violation-feed">
            <div className="feed-header">
                <div className="feed-title-wrapper">
                    <h3>Live Violation Feed</h3>
                    <span className="live-pulse"></span>
                </div>
                <span className="violation-count">{violations.length} active alerts</span>
            </div>
            <div className="violations-list">
                {violations.length === 0 ? (
                    <div className="empty-feed">
                        <div className="shield-placeholder">🛡️</div>
                        <p>No violations detected in the current session.</p>
                        <small>AI monitoring system is active and scanning...</small>
                    </div>
                ) : (
                    violations.map(v => (
                        <ViolationCard key={v.event_id || Math.random()} violation={v} />
                    ))
                )}
            </div>
        </div>
    );
}
