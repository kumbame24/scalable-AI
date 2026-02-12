import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import { Plus, List, Search, Calendar, Clock, BookOpen } from 'lucide-react';

export default function Settings() {
    const { token } = useAuth();
    const [title, setTitle] = useState('');
    const [courseCode, setCourseCode] = useState('');
    const [duration, setDuration] = useState(120);
    const [exams, setExams] = useState([]);
    const [searchTerm, setSearchTerm] = useState('');
    const [message, setMessage] = useState({ type: '', text: '' });

    const fetchExams = async () => {
        try {
            const response = await fetch('http://localhost:8000/examinations');
            if (response.ok) {
                const data = await response.json();
                setExams(data);
            }
        } catch (error) {
            console.error("Error fetching exams:", error);
        }
    };

    useEffect(() => {
        fetchExams();
    }, []);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setMessage({ type: '', text: '' });
        try {
            const response = await fetch('http://localhost:8000/examinations', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    title,
                    course_code: courseCode,
                    duration_minutes: parseInt(duration)
                })
            });

            if (response.ok) {
                setMessage({ type: 'success', text: 'Examination created successfully!' });
                setTitle('');
                setCourseCode('');
                fetchExams();
            } else {
                const data = await response.json();
                setMessage({ type: 'error', text: data.detail || 'Failed to create examination.' });
            }
        } catch (error) {
            setMessage({ type: 'error', text: 'Error connecting to server.' });
        }
    };

    const filteredExams = exams.filter(exam =>
        exam.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        exam.course_code.toLowerCase().includes(searchTerm.toLowerCase())
    );

    return (
        <div className="dashboard-content">
            <div className="content-wrapper">
                <div className="page-header-flex">
                    <div>
                        <h2 className="page-title">Configuration</h2>
                        <p className="page-subtitle">Manage examination entries, start sessions, and view recent logs.</p>
                    </div>
                </div>

                <div className="settings-grid">
                    <div className="settings-card">
                        <div className="card-header">
                            <Plus size={20} className="icon-blue" />
                            <h3>Create New Examination</h3>
                        </div>
                        <form onSubmit={handleSubmit} className="entry-form">
                            {message.text && (
                                <div className={`form-message ${message.type}`}>
                                    {message.text}
                                </div>
                            )}
                            <div className="form-row">
                                <div className="form-field">
                                    <label>Examination Title</label>
                                    <input
                                        type="text"
                                        value={title}
                                        onChange={(e) => setTitle(e.target.value)}
                                        placeholder="e.g. Final Midterm"
                                        required
                                    />
                                </div>
                                <div className="form-field">
                                    <label>Course Code</label>
                                    <input
                                        type="text"
                                        value={courseCode}
                                        onChange={(e) => setCourseCode(e.target.value)}
                                        placeholder="e.g. CS101"
                                        required
                                    />
                                </div>
                            </div>
                            <div className="form-field">
                                <label>Duration (Minutes)</label>
                                <input
                                    type="number"
                                    value={duration}
                                    onChange={(e) => setDuration(e.target.value)}
                                    required
                                />
                            </div>
                            <button type="submit" className="primary-btn">Start Examination</button>
                        </form>
                    </div>

                    <div className="settings-card">
                        <div className="card-header" style={{ justifyContent: 'space-between' }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                                <List size={20} className="icon-blue" />
                                <h3>Recent Examinations</h3>
                            </div>
                            <div className="search-container" style={{ width: '200px' }}>
                                <Search size={14} className="search-icon" />
                                <input
                                    type="text"
                                    className="search-input"
                                    style={{ padding: '6px 8px', fontSize: '13px' }}
                                    placeholder="Filter list..."
                                    value={searchTerm}
                                    onChange={(e) => setSearchTerm(e.target.value)}
                                />
                            </div>
                        </div>
                        <div className="exams-list">
                            {filteredExams.length === 0 ? (
                                <p className="empty-msg">No examinations found.</p>
                            ) : (
                                filteredExams.map(exam => (
                                    <div key={exam.id} className="exam-item">
                                        <div className="exam-info">
                                            <strong>{exam.course_code}: {exam.title}</strong>
                                            <div style={{ display: 'flex', gap: '12px', marginTop: '4px' }}>
                                                <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                                                    <Calendar size={12} /> {new Date(exam.start_time).toLocaleDateString()}
                                                </span>
                                                <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                                                    <Clock size={12} /> {exam.duration_minutes}m
                                                </span>
                                            </div>
                                        </div>
                                        {exam.is_active === 1 ? (
                                            <span className="role-tag active">Active</span>
                                        ) : (
                                            <span className="role-tag completed">Logged</span>
                                        )}
                                    </div>
                                ))
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
