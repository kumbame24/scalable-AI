import React, { useState, useEffect } from 'react';
import { FileText, Download, Calendar, Clock, Activity } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

export default function Reports() {
    const { token } = useAuth();
    const [exams, setExams] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchExams = async () => {
            try {
                const response = await fetch('http://localhost:8000/examinations', {
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                if (response.ok) {
                    const data = await response.json();
                    setExams(data);
                }
            } catch (error) {
                console.error("Error fetching exams:", error);
            } finally {
                setLoading(false);
            }
        };
        if (token) fetchExams();
    }, [token]);

    const handleDownload = (examId) => {
        window.open(`http://localhost:8000/session/${examId}/export`, "_blank");
    };

    return (
        <div className="dashboard-content">
            <div className="content-wrapper">
                <div className="page-header-flex">
                    <div>
                        <h2 className="page-title">Examination Reports</h2>
                        <p className="page-subtitle">Access historical session data and download detailed integrity reports.</p>
                    </div>
                    <div className="quick-stats-mini">
                        <div className="mini-stat">
                            <span className="mini-label">Total Examinations</span>
                            <span className="mini-value text-emerald">{exams.length}</span>
                        </div>
                    </div>
                </div>

                <div className="data-card">
                    {loading ? (
                        <div className="loading-state">Loading examination records...</div>
                    ) : exams.length === 0 ? (
                        <div className="empty-state">No examination records found.</div>
                    ) : (
                        <table className="data-table">
                            <thead>
                                <tr>
                                    <th>Exam Title</th>
                                    <th>Course Code</th>
                                    <th>Date</th>
                                    <th>Duration</th>
                                    <th>Status</th>
                                    <th>Action</th>
                                </tr>
                            </thead>
                            <tbody>
                                {exams.map((exam) => (
                                    <tr key={exam.id}>
                                        <td className="font-bold">{exam.title}</td>
                                        <td>{exam.course_code}</td>
                                        <td>{new Date(exam.start_time).toLocaleDateString()}</td>
                                        <td>{exam.duration_minutes} min</td>
                                        <td>
                                            {exam.is_active ? (
                                                <span className="role-tag active">Active Now</span>
                                            ) : (
                                                <span className="role-tag completed">Completed</span>
                                            )}
                                        </td>
                                        <td>
                                            <button
                                                className="btn-download"
                                                onClick={() => handleDownload(exam.id)}
                                            >
                                                <Download size={14} /> CSV Report
                                            </button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    )}
                </div>
            </div>
        </div>
    );
}
