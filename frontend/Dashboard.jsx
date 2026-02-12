import { useEffect, useState } from "react";
import AlertPanel from "./components/AlertPanel";
import LiveFeed from "./components/LiveFeed";
import Sidebar from "./components/Sidebar";
import "./styles.css";

function Dashboard() {
    const [alerts, setAlerts] = useState([]);
    const [stats, setStats] = useState(null);
    const [loading, setLoading] = useState(false);
    const [sessionId, setSessionId] = useState(1);
    const [filter, setFilter] = useState({
        confidence: 0.65,
        sourceFilter: "all"
    });

    // Fetch alerts
    useEffect(() => {
        const fetchAlerts = async () => {
            try {
                setLoading(true);
                const response = await fetch(
                    `http://localhost:8000/alerts?confidence=${filter.confidence}&limit=50`,
                    { headers: { "Content-Type": "application/json" } }
                );
                if (response.ok) {
                    let data = await response.json();
                    
                    // Filter by source if needed
                    if (filter.sourceFilter !== "all") {
                        data = data.filter(a => a.source === filter.sourceFilter);
                    }
                    
                    setAlerts(data);
                }
            } catch (error) {
                console.error("Error fetching alerts:", error);
            } finally {
                setLoading(false);
            }
        };

        const interval = setInterval(fetchAlerts, 1000);
        fetchAlerts(); // Initial fetch
        return () => clearInterval(interval);
    }, [filter]);

    // Fetch session statistics
    useEffect(() => {
        const fetchStats = async () => {
            try {
                const response = await fetch(
                    `http://localhost:8000/session/${sessionId}/stats`
                );
                if (response.ok) {
                    const data = await response.json();
                    setStats(data);
                }
            } catch (error) {
                console.error("Error fetching stats:", error);
            }
        };

        const interval = setInterval(fetchStats, 5000);
        fetchStats(); // Initial fetch
        return () => clearInterval(interval);
    }, [sessionId]);

    const handleConfidenceChange = (value) => {
        setFilter({ ...filter, confidence: parseFloat(value) });
    };

    const handleSourceFilter = (source) => {
        setFilter({ ...filter, sourceFilter: source });
    };

    return (
        <div className="dashboard-container">
            <Sidebar 
                sessionId={sessionId}
                onSessionChange={setSessionId}
                stats={stats}
            />
            <div className="main-content">
                <header className="dashboard-header">
                    <h1>Exam Monitoring Dashboard</h1>
                    <div className="header-controls">
                        <div className="control-group">
                            <label htmlFor="confidence-slider">
                                Confidence Threshold:
                            </label>
                            <input
                                id="confidence-slider"
                                type="range"
                                min="0"
                                max="1"
                                step="0.05"
                                value={filter.confidence}
                                onChange={(e) => handleConfidenceChange(e.target.value)}
                                className="slider"
                            />
                            <span>{(filter.confidence * 100).toFixed(0)}%</span>
                        </div>
                        <div className="control-group">
                            <label>Filter by Source:</label>
                            <select 
                                value={filter.sourceFilter}
                                onChange={(e) => handleSourceFilter(e.target.value)}
                                className="source-select"
                            >
                                <option value="all">All Sources</option>
                                <option value="video">Video Only</option>
                                <option value="audio">Audio Only</option>
                            </select>
                        </div>
                    </div>
                </header>

                <div className="dashboard-content">
                    <section className="video-section">
                        <h2>Live Feed</h2>
                        <LiveFeed />
                    </section>

                    <section className="alerts-section">
                        <h2>
                            Detected Events
                            {loading && <span className="loading-indicator">Loading...</span>}
                        </h2>
                        {alerts.length === 0 ? (
                            <div className="empty-state">
                                <p>No events detected at this threshold</p>
                            </div>
                        ) : (
                            <div className="alerts-grid">
                                {alerts.map((alert, index) => (
                                    <AlertPanel key={index} alert={alert} />
                                ))}
                            </div>
                        )}
                    </section>
                </div>
            </div>
        </div>
    );
}

export default Dashboard;

