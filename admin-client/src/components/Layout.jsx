import React from 'react';
import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom';
import { LogOut, CheckCircle, User, Settings, AlertTriangle } from 'lucide-react';
import '../pages/Dashboard.css'; // Reuse dashboard styles for layout

function Layout() {
    const location = useLocation();
    const navigate = useNavigate();

    const handleLogout = () => {
        localStorage.removeItem('token');
        navigate('/login');
    };

    return (
        <div className="dashboard-layout">
            <aside className="sidebar">
                <div className="sidebar-header">
                    <h2>Attendance Admin</h2>
                </div>
                <nav className="sidebar-nav">
                    <Link to="/dashboard" className={location.pathname === '/dashboard' ? 'active' : ''}>
                        <CheckCircle size={20} /> ダッシュボード
                    </Link>
                    <Link to="/students" className={location.pathname === '/students' ? 'active' : ''}>
                        <User size={20} /> 学生一覧
                    </Link>
                    <Link to="/reports" className={location.pathname === '/reports' ? 'active' : ''}>
                        <AlertTriangle size={20} /> レポート
                    </Link>
                    <a href="#"><Settings size={20} /> 設定</a>
                </nav>
                <div className="sidebar-footer">
                    <button onClick={handleLogout} className="logout-btn">
                        <LogOut size={18} /> ログアウト
                    </button>
                </div>
            </aside>

            <main className="main-content">
                <header className="top-header">
                    <h1>{location.pathname === '/dashboard' ? 'ダッシュボード' :
                        location.pathname === '/students' ? '学生一覧' :
                            location.pathname === '/reports' ? 'レポート' : '管理画面'}</h1>
                    <div className="user-info">
                        <span>管理者: <strong>Admin Teacher</strong></span>
                    </div>
                </header>

                <Outlet />
            </main>
        </div>
    );
}

export default Layout;
