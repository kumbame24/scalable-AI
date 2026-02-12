import React, { useState, useEffect } from 'react';
import { Users, Mail, Calendar, ShieldCheck, Search, Plus, X, UserPlus, ShieldAlert } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

export default function Students() {
    const { token, register } = useAuth();
    const [students, setStudents] = useState([]);
    const [filteredStudents, setFilteredStudents] = useState([]);
    const [searchTerm, setSearchTerm] = useState('');
    const [loading, setLoading] = useState(true);
    const [showModal, setShowModal] = useState(false);

    // Form state
    const [formData, setFormData] = useState({ username: '', email: '', password: '' });
    const [formMsg, setFormMsg] = useState({ type: '', text: '' });
    const [isSubmitting, setIsSubmitting] = useState(false);

    const fetchStudents = async () => {
        setLoading(true);
        try {
            const response = await fetch('http://localhost:8000/users?role=student', {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (response.ok) {
                const data = await response.json();
                setStudents(data);
                setFilteredStudents(data);
            }
        } catch (error) {
            console.error("Error fetching students:", error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        if (token) fetchStudents();
    }, [token]);

    useEffect(() => {
        const results = students.filter(student =>
            student.username.toLowerCase().includes(searchTerm.toLowerCase()) ||
            student.email.toLowerCase().includes(searchTerm.toLowerCase())
        );
        setFilteredStudents(results);
    }, [searchTerm, students]);

    const handleAddStudent = async (e) => {
        e.preventDefault();
        setFormMsg({ type: '', text: '' });
        setIsSubmitting(true);

        try {
            const success = await register(formData.username, formData.email, formData.password, "student");
            if (success) {
                setFormMsg({ type: 'success', text: 'Student registered successfully!' });
                setFormData({ username: '', email: '', password: '' });
                setTimeout(() => {
                    setShowModal(false);
                    setFormMsg({ type: '', text: '' });
                    fetchStudents();
                }, 1500);
            } else {
                setFormMsg({ type: 'error', text: 'Failed to register student. Email or username might be taken.' });
            }
        } catch (error) {
            setFormMsg({ type: 'error', text: 'Connection error. Please try again.' });
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <div className="dashboard-content">
            <div className="content-wrapper">
                <div className="page-header-flex">
                    <div>
                        <h2 className="page-title">Student Directory</h2>
                        <p className="page-subtitle">Manage enrolled students and monitor their registration status.</p>
                    </div>
                    <div className="quick-stats-mini">
                        <div className="search-container">
                            <Search size={18} className="search-icon" />
                            <input
                                type="text"
                                className="search-input"
                                placeholder="Search students..."
                                value={searchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                            />
                        </div>
                        <button className="btn-add-student" onClick={() => setShowModal(true)}>
                            <Plus size={18} /> Add Student
                        </button>
                    </div>
                </div>

                <div className="data-card">
                    {loading ? (
                        <div className="loading-state">Loading students...</div>
                    ) : filteredStudents.length === 0 ? (
                        <div className="empty-state">
                            {searchTerm ? `No students matching "${searchTerm}"` : 'No students found in the database.'}
                        </div>
                    ) : (
                        <table className="data-table">
                            <thead>
                                <tr>
                                    <th>Student Name</th>
                                    <th>Email Address</th>
                                    <th>Role</th>
                                    <th>Registration Date</th>
                                    <th>Status</th>
                                </tr>
                            </thead>
                            <tbody>
                                {filteredStudents.map((student) => (
                                    <tr key={student.id}>
                                        <td className="font-bold">{student.username}</td>
                                        <td>{student.email}</td>
                                        <td><span className="role-tag student">Student</span></td>
                                        <td>{new Date(student.created_at).toLocaleDateString()}</td>
                                        <td>
                                            <span className="status-badge active">
                                                <ShieldCheck size={12} /> Verified
                                            </span>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    )}
                </div>
            </div>

            {/* Registration Modal */}
            {showModal && (
                <div className="modal-overlay">
                    <div className="modal-content animate-slide-in">
                        <div className="modal-header">
                            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                                <UserPlus size={24} color="#6366f1" />
                                <h3>Register New Student</h3>
                            </div>
                            <button className="close-btn" onClick={() => setShowModal(false)}>
                                <X size={20} />
                            </button>
                        </div>

                        <form onSubmit={handleAddStudent} className="entry-form">
                            {formMsg.text && (
                                <div className={`form-message ${formMsg.type}`}>
                                    {formMsg.text}
                                </div>
                            )}

                            <div className="form-field">
                                <label>Full Name</label>
                                <input
                                    type="text"
                                    placeholder="e.g. John Doe"
                                    value={formData.username}
                                    onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                                    required
                                />
                            </div>

                            <div className="form-field">
                                <label>Institutional Email</label>
                                <input
                                    type="email"
                                    placeholder="john.doe@university.edu"
                                    value={formData.email}
                                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                                    required
                                />
                            </div>

                            <div className="form-field">
                                <label>Initial Password</label>
                                <input
                                    type="password"
                                    placeholder="••••••••"
                                    value={formData.password}
                                    onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                                    required
                                />
                                <span style={{ fontSize: '11px', color: '#94a3b8', marginTop: '4px' }}>
                                    <ShieldAlert size={10} style={{ marginRight: '4px' }} />
                                    Temporary password for student's first login.
                                </span>
                            </div>

                            <button type="submit" className="primary-btn" disabled={isSubmitting}>
                                {isSubmitting ? 'Registering...' : 'Register Student'}
                            </button>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
}
