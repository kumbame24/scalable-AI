import { Routes, Route } from 'react-router-dom';
import Header from "./components/Header";
import Sidebar from "./components/Sidebar";
import Dashboard from "./components/pages/Dashboard";
import Students from "./components/pages/Students";
import Reports from "./components/pages/Reports";
import Settings from "./components/pages/Settings";
import Profile from "./components/pages/Profile";
import Login from "./components/pages/Login";
import Register from "./components/pages/Register";
import LiveFeed from "./components/LiveFeed";
import ViolationFeed from "./components/ViolationFeed";
import { useAuth } from './context/AuthContext';
import { Navigate } from 'react-router-dom';

// Wrapper for the dashboard content to reuse the layout
const DashboardLayout = ({ children }) => (
    <div className="dashboard-content">
        <div className="content-wrapper">
            {children}
        </div>
    </div>
);

export default function App() {
    const { user, loading } = useAuth();

    if (loading) return <div className="loading-screen">Loading (System Initializing)...</div>;

    const ProtectedRoute = ({ children }) => {
        return user ? children : <Navigate to="/login" />;
    };

    return (
        <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="*" element={
                <ProtectedRoute>
                    <div className="layout">
                        <Sidebar />
                        <div className="main-content">
                            <Header />
                            <Routes>
                                <Route path="/" element={<Dashboard />} />
                                <Route path="/live" element={
                                    <DashboardLayout>
                                        <h2 className="page-title">Live Monitoring</h2>
                                        <div className="dashboard-grid">
                                            <LiveFeed />
                                            <ViolationFeed />
                                        </div>
                                    </DashboardLayout>
                                } />
                                <Route path="/alerts" element={
                                    <DashboardLayout>
                                        <h2 className="page-title">Alerts & Events</h2>
                                        <ViolationFeed />
                                    </DashboardLayout>
                                } />
                                <Route path="/students" element={<Students />} />
                                <Route path="/reports" element={<Reports />} />
                                <Route path="/configuration" element={<Settings />} />
                                <Route path="/profile" element={<Profile />} />
                            </Routes>
                        </div>
                    </div>
                </ProtectedRoute>
            } />
        </Routes>
    );
}
