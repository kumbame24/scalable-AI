import StatsRow from "../StatsRow";
import LiveFeed from "../LiveFeed";
import ViolationFeed from "../ViolationFeed";
import SessionSummary from "../SessionSummary";

export default function Dashboard() {
    return (
        <div className="dashboard-content">
            <div className="content-wrapper">
                <h2 className="page-title">Dashboard Overview</h2>
                <p className="page-subtitle">Real-time monitoring and AI integrity analysis.</p>

                <StatsRow />

                <div className="dashboard-grid">
                    <div className="monitoring-main">
                        <LiveFeed />
                        <SessionSummary />
                    </div>
                    <ViolationFeed />
                </div>
            </div>
        </div>
    );
}
