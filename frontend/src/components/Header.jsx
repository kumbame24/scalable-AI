import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Bell, Search, Clock } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export default function Header() {
    const { user } = useAuth();
    const [activeExam, setActiveExam] = useState(null);
    const [timeLeft, setTimeLeft] = useState("");

    // Fetch active examination
    useEffect(() => {
        const fetchActiveExam = async () => {
            try {
                const response = await fetch('http://localhost:8000/examinations/active');
                if (response.ok) {
                    const data = await response.json();
                    setActiveExam(data);
                }
            } catch (error) {
                console.error("Error fetching active exam:", error);
            }
        };
        fetchActiveExam();
        const interval = setInterval(fetchActiveExam, 30000); // Update every 30s
        return () => clearInterval(interval);
    }, []);

    // Countdown Timer Logic
    useEffect(() => {
        if (!activeExam) return;

        const calculateTime = () => {
            const start = new Date(activeExam.start_time).getTime();
            const durationMs = activeExam.duration_minutes * 60 * 1000;
            const end = start + durationMs;
            const now = new Date().getTime();
            const diff = end - now;

            if (diff <= 0) {
                setTimeLeft("00:00:00 Remaining");
                return;
            }

            const h = Math.floor(diff / (1000 * 60 * 60));
            const m = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
            const s = Math.floor((diff % (1000 * 60)) / 1000);

            const pad = (n) => n.toString().padStart(2, '0');
            setTimeLeft(`${pad(h)}:${pad(m)}:${pad(s)} Remaining`);
        };

        calculateTime();
        const interval = setInterval(calculateTime, 1000);
        return () => clearInterval(interval);
    }, [activeExam]);

    const getInitials = (name) => {
        if (!name) return "??";
        return name.split(' ').map(n => n[0]).join('').toUpperCase().substring(0, 2);
    };

    return (
        <header className="header">
            <div className="header-left">
                <span className="breadcrumb">Examinations</span>
                <span className="breadcrumb-separator">›</span>
                <span className="breadcrumb-current">
                    {activeExam ? `${activeExam.course_code}: ${activeExam.title}` : "Loading Examination..."}
                </span>
            </div>

            <div className="header-center">
                <div className="exam-timer">
                    <Clock size={16} className="timer-icon" />
                    <span className="timer-text">{timeLeft || "Calculating..."}</span>
                </div>
                <div className="search-bar">
                    <Search size={16} className="search-icon" />
                    <input type="text" placeholder="Search students..." />
                </div>
            </div>

            <div className="header-right">
                <button className="icon-btn">
                    <Bell size={20} />
                    <span className="notification-dot"></span>
                </button>
                <Link to="/profile" className="user-profile-link">
                    <div className="user-profile">
                        <div className="user-info">
                            <span className="user-name">{user?.username || "Guest User"}</span>
                            <span className="user-role">
                                {user?.role === 'admin' ? 'Chief Proctor' : 'Invigilator'}
                            </span>
                        </div>
                        <div className="user-avatar">{getInitials(user?.username)}</div>
                    </div>
                </Link>
            </div>
        </header>
    );
}
