import React, { useState, useEffect } from "react";
import { CheckCircle, Download, AlertCircle, FileText } from "lucide-react";
import { useAuth } from "../context/AuthContext";

export default function SessionSummary() {
    const { token } = useAuth();
    const [activeExam, setActiveExam] = useState(null);
    const [stats, setStats] = useState(null);
    const [isFinalizing, setIsFinalizing] = useState(false);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const examRes = await fetch("http://localhost:8000/examinations/active");
                if (examRes.ok) {
                    const exam = await examRes.json();
                    setActiveExam(exam);
                    if (exam) {
                        const statsRes = await fetch(`http://localhost:8000/session/${exam.id}/stats`);
                        if (statsRes.ok) {
                            setStats(await statsRes.json());
                        }
                    }
                }
            } catch (err) {
                console.error("Failed to fetch session data:", err);
            }
        };
        fetchData();
    }, []);

    const handleFinalize = async () => {
        if (!activeExam) return;
        if (!window.confirm("Are you sure you want to finalize this examination? This will stop all AI monitoring.")) return;

        setIsFinalizing(true);
        try {
            const res = await fetch(`http://localhost:8000/examinations/${activeExam.id}/finalize`, {
                method: "POST",
                headers: {
                    "Authorization": `Bearer ${token}`
                }
            });
            if (res.ok) {
                alert("Examination finalized successfully.");
                window.location.reload();
            } else {
                const err = await res.json();
                alert(`Error: ${err.detail || "Failed to finalize"}`);
            }
        } catch (err) {
            console.error("Finalization failed:", err);
        } finally {
            setIsFinalizing(false);
        }
    };

    const handleExport = async () => {
        if (!activeExam) return;
        window.open(`http://localhost:8000/session/${activeExam.id}/export`, "_blank");
    };

    if (!activeExam) return null;

    return (
        <div className="session-summary-card">
            <div className="summary-header">
                <div className="header-info">
                    <FileText size={20} color="#6366f1" />
                    <h3>Session Integrity Report</h3>
                </div>
                <button
                    className="btn-finalize"
                    onClick={handleFinalize}
                    disabled={isFinalizing}
                >
                    {isFinalizing ? "Processing..." : "Finalize Examination"}
                </button>
            </div>

            <div className="summary-grid">
                <div className="summary-item">
                    <span className="label">Course</span>
                    <span className="value">{activeExam.course_code}</span>
                </div>
                <div className="summary-item">
                    <span className="label">Title</span>
                    <span className="value">{activeExam.title}</span>
                </div>
                <div className="summary-item">
                    <span className="label">Detections</span>
                    <span className={`value ${stats?.total_events > 20 ? 'warning' : ''}`}>
                        {stats?.total_events || 0}
                    </span>
                </div>
                <div className="summary-item">
                    <span className="label">Stability Score</span>
                    <span className="value">
                        {stats?.average_confidence ? (stats.average_confidence * 100).toFixed(1) + "%" : "N/A"}
                    </span>
                </div>
            </div>

            <div className="violation-breakdown">
                <h4>Violation Breakdown</h4>
                {stats?.event_types && Object.keys(stats.event_types).length > 0 ? (
                    <div className="breakdown-tags">
                        {Object.entries(stats.event_types).map(([type, count]) => (
                            <div key={type} className="breakdown-tag">
                                <span className="tag-name">{type.replace(/_/g, ' ')}</span>
                                <span className="tag-count">{count}</span>
                            </div>
                        ))}
                    </div>
                ) : (
                    <p className="no-data">No specific violations recorded for breakdown.</p>
                )}
            </div>

            <div className="summary-footer">
                <button className="btn-secondary-slim" onClick={handleExport}>
                    <Download size={14} /> Export CSV
                </button>
                <div className="auto-save-indicator">
                    <CheckCircle size={12} color="#10B981" />
                    <span>Auto-saved to cloud</span>
                </div>
            </div>
        </div>
    );
}
