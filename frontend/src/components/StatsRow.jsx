import React, { useState, useEffect } from 'react';
import { Users, Activity, ShieldAlert, Cpu } from 'lucide-react';

const StatCard = ({ title, value, trend, trendUp, icon: Icon, iconColor, iconBg, trendData = [40, 70, 45, 90, 65, 80, 50] }) => (
    <div className="stat-card">
        <div className="stat-header">
            <div className="stat-icon" style={{ backgroundColor: iconBg }}>
                <Icon size={20} color={iconColor} />
            </div>
            {trend && (
                <span className={`stat-trend ${trendUp ? 'trend-up' : 'trend-down'}`}>
                    {trend}
                </span>
            )}
        </div>
        <div className="stat-content">
            <h3>{title}</h3>
            <p className="stat-number">{value}</p>
        </div>
        <div className="stat-footer-trend">
            <div className="trend-graph">
                {trendData.map((val, i) => (
                    <div
                        key={i}
                        className={`trend-bar ${i === trendData.length - 1 ? (trendUp ? 'active' : 'warning') : ''}`}
                        style={{ height: `${val}%` }}
                    />
                ))}
            </div>
        </div>
    </div>
);

export default function StatsRow() {
    const [stats, setStats] = useState({
        totalStudents: 128,
        activeSessions: 0,
        detectedViolations: 0,
        criticalAlerts: 0
    });

    useEffect(() => {
        const fetchStats = async () => {
            try {
                // 1. Fetch student count
                const userRes = await fetch('http://localhost:8000/users/count?role=student');
                if (userRes.ok) {
                    const userData = await userRes.json();
                    setStats(prev => ({ ...prev, totalStudents: userData.count }));
                }

                // 2. Check if an exam is active
                const examRes = await fetch('http://localhost:8000/examinations/active');
                if (examRes.ok) {
                    const activeExam = await examRes.json();
                    if (activeExam) {
                        const statsRes = await fetch(`http://localhost:8000/session/${activeExam.id}/stats`);
                        if (statsRes.ok) {
                            const data = await statsRes.json();
                            setStats(prev => ({
                                ...prev,
                                activeSessions: 1,
                                detectedViolations: data.total_events || 0,
                                criticalAlerts: data.high_confidence_events || 0
                            }));
                        }
                    } else {
                        setStats(prev => ({ ...prev, activeSessions: 0 }));
                    }
                }
            } catch (error) {
                console.error("Error fetching stats:", error);
            }
        };

        fetchStats();
        const interval = setInterval(fetchStats, 5000);
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="stats-row">
            <StatCard
                title="Total Students"
                value={stats.totalStudents}
                trend="+12%"
                trendUp={true}
                icon={Users}
                iconColor="#2563EB"
                iconBg="#EBF2FE"
            />
            <StatCard
                title="Active Sessions"
                value={stats.activeSessions}
                trend={stats.activeSessions > 0 ? "LIVE" : "OFF"}
                trendUp={stats.activeSessions > 0}
                icon={Activity}
                iconColor="#10B981"
                iconBg="#D1FAE5"
            />
            <StatCard
                title="Total Detections"
                value={stats.detectedViolations}
                trend="Real-time"
                trendUp={true}
                icon={Cpu}
                iconColor="#F59E0B"
                iconBg="#FEF3C7"
            />
            <StatCard
                title="Critical Alerts"
                value={stats.criticalAlerts}
                trend={stats.criticalAlerts > 5 ? "High" : "Stable"}
                trendUp={stats.criticalAlerts <= 5}
                icon={ShieldAlert}
                iconColor="#EF4444"
                iconBg="#FEE2E2"
            />
        </div>
    );
}
