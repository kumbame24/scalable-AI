import React from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Users, AlertTriangle, FileText, Settings, Shield, Video, User } from 'lucide-react';

import { useAuth } from '../context/AuthContext';

export default function Sidebar() {
    const { user } = useAuth();
    const isAdmin = user?.role === 'admin';
    return (
        <div className="sidebar">
            <div className="sidebar-header">
                <div className="logo-container">
                    <Shield className="logo-icon" size={24} />
                    <h2>Exam AI Monitor</h2>
                </div>
            </div>

            <div className="sidebar-section-label">MAIN MENU</div>
            <nav className="sidebar-nav">
                <NavLink to="/" className={({ isActive }) => isActive ? "active" : ""}>
                    <LayoutDashboard size={20} />
                    <span>Dashboard</span>
                </NavLink>
                <NavLink to="/live" className={({ isActive }) => isActive ? "active" : ""}>
                    <Video size={20} />
                    <span>Live Monitoring</span>
                </NavLink>
                <NavLink to="/alerts" className={({ isActive }) => isActive ? "active" : ""}>
                    <AlertTriangle size={20} />
                    <span>Alerts & Events</span>
                </NavLink>
                <NavLink to="/students" className={({ isActive }) => isActive ? "active" : ""}>
                    <Users size={20} />
                    <span>Student List</span>
                </NavLink>
                <NavLink to="/reports" className={({ isActive }) => isActive ? "active" : ""}>
                    <FileText size={20} />
                    <span>Reports</span>
                </NavLink>
                <NavLink to="/profile" className={({ isActive }) => isActive ? "active" : ""}>
                    <User size={20} />
                    <span>My Profile</span>
                </NavLink>
            </nav>

            {isAdmin && (
                <>
                    <div className="sidebar-section-label system-label">SYSTEM</div>
                    <nav className="sidebar-nav">
                        <NavLink to="/configuration" className={({ isActive }) => isActive ? "active" : ""}>
                            <Settings size={20} />
                            <span>Configuration</span>
                        </NavLink>
                    </nav>
                </>
            )}
        </div>
    );
}
