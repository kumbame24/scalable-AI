import React from 'react';
import { useAuth } from '../../context/AuthContext';
import { User, Mail, Shield, Calendar, Fingerprint, Clock } from 'lucide-react';

export default function Profile() {
    const { user } = useAuth();

    if (!user) return <div className="loading-screen">Loading Profile...</div>;

    const formatDate = (dateString) => {
        if (!dateString) return "N/A";
        return new Date(dateString).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    };

    const getAccountAge = (dateString) => {
        if (!dateString) return "N/A";
        const created = new Date(dateString);
        const now = new Date();
        const diffDays = Math.floor((now - created) / (1000 * 60 * 60 * 24));
        if (diffDays === 0) return "Created Today";
        return `Member for ${diffDays} day${diffDays > 1 ? 's' : ''}`;
    };

    return (
        <div className="dashboard-content">
            <div className="content-wrapper">
                <div className="page-header-flex">
                    <div>
                        <h2 className="page-title">Personal Profile</h2>
                        <p className="page-subtitle">Your account information from the secure PostgreSQL database.</p>
                    </div>
                </div>

                <div className="settings-grid">
                    <div className="settings-card data-card">
                        <div className="card-header">
                            <User className="icon-blue" size={20} />
                            <h3>Account Overview</h3>
                        </div>

                        <div className="profile-details">
                            <div className="detail-item">
                                <div className="detail-icon">
                                    <Fingerprint size={18} />
                                </div>
                                <div className="detail-content">
                                    <label>Internal User ID</label>
                                    <p className="mono">#{user.id}</p>
                                </div>
                            </div>

                            <div className="detail-item">
                                <div className="detail-icon">
                                    <User size={18} />
                                </div>
                                <div className="detail-content">
                                    <label>Username</label>
                                    <p>{user.username}</p>
                                </div>
                            </div>

                            <div className="detail-item">
                                <div className="detail-icon">
                                    <Mail size={18} />
                                </div>
                                <div className="detail-content">
                                    <label>Email Address</label>
                                    <p>{user.email}</p>
                                </div>
                            </div>

                            <div className="detail-item">
                                <div className="detail-icon">
                                    <Shield size={18} />
                                </div>
                                <div className="detail-content">
                                    <label>System Role</label>
                                    <span className={`status-badge ${user.role === 'admin' ? 'active' : ''}`}>
                                        {user.role === 'admin' ? 'Chief Proctor' : 'Invigilator'}
                                    </span>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div className="settings-card data-card">
                        <div className="card-header">
                            <Calendar className="icon-blue" size={20} />
                            <h3>Security & Activity</h3>
                        </div>

                        <div className="profile-details">
                            <div className="detail-item">
                                <div className="detail-icon">
                                    <Calendar size={18} />
                                </div>
                                <div className="detail-content">
                                    <label>Date Registered</label>
                                    <p>{formatDate(user.created_at)}</p>
                                </div>
                            </div>

                            <div className="detail-item">
                                <div className="detail-icon">
                                    <Clock size={18} />
                                </div>
                                <div className="detail-content">
                                    <label>Account Age</label>
                                    <p>{getAccountAge(user.created_at)}</p>
                                </div>
                            </div>

                            <div className="detail-item">
                                <div className="detail-icon">
                                    <Shield size={18} />
                                </div>
                                <div className="detail-content">
                                    <label>Status</label>
                                    <span className="status-badge" style={{ background: '#ECFDF5', color: '#059669' }}>Verified Account</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <style>{`
                .profile-details {
                    display: flex;
                    flex-direction: column;
                    gap: 20px;
                }
                .detail-item {
                    display: flex;
                    gap: 16px;
                    align-items: flex-start;
                    padding-bottom: 20px;
                    border-bottom: 1px solid #f1f5f9;
                }
                .detail-item:last-child {
                    border-bottom: none;
                }
                .detail-icon {
                    width: 36px;
                    height: 36px;
                    background: #f8fafc;
                    border-radius: 8px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    color: #64748b;
                }
                .detail-content label {
                    display: block;
                    font-size: 11px;
                    font-weight: 600;
                    text-transform: uppercase;
                    color: #94a3b8;
                    margin-bottom: 4px;
                    letter-spacing: 0.05em;
                }
                .detail-content p {
                    font-weight: 500;
                    color: #1e293b;
                }
                .detail-content p.mono {
                    font-family: 'JetBrains Mono', 'Fira Code', monospace;
                    font-size: 13px;
                }
            `}</style>
        </div>
    );
}
