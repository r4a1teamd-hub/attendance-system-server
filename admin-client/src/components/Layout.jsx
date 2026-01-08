import React, { useState } from 'react';
import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom';
import { LogOut, CheckCircle, User, Settings, AlertTriangle, Calendar, Menu, ChevronLeft } from 'lucide-react';
import '../pages/Dashboard.css'; // Reuse dashboard styles for layout

function Layout() {
    const location = useLocation();
    const navigate = useNavigate();
    const [collapsed, setCollapsed] = useState(false);

    const handleLogout = () => {
        localStorage.removeItem('token');
        navigate('/login');
    };

    return (
        <div className="dashboard-layout">
            <aside className={`sidebar ${collapsed ? 'collapsed' : ''}`}>
                <div className="sidebar-header">
                    <div className="header-content">
                        {!collapsed && <h2>Attendance Admin</h2>}
                        <button
                            className="toggle-btn"
                            onClick={() => setCollapsed(!collapsed)}
                            title={collapsed ? "メニューを展開" : "メニューを折りたたむ"}
                        >
                            {collapsed ? <Menu size={20} /> : <ChevronLeft size={20} />}
                        </button>
                    </div>
                </div>
                <nav className="sidebar-nav">
                    <Link to="/dashboard" className={location.pathname === '/dashboard' ? 'active' : ''} title="ダッシュボード">
                        <CheckCircle size={20} />
                        {!collapsed && <span>ダッシュボード</span>}
                    </Link>
                    <Link to="/attendance-register" className={location.pathname === '/attendance-register' ? 'active' : ''} title="出席簿">
                        <Calendar size={20} />
                        {!collapsed && <span>出席簿</span>}
                    </Link>
                    <Link to="/students" className={location.pathname === '/students' ? 'active' : ''} title="学生一覧">
                        <User size={20} />
                        {!collapsed && <span>学生一覧</span>}
                    </Link>
                    <Link to="/reports" className={location.pathname === '/reports' ? 'active' : ''} title="レポート">
                        <AlertTriangle size={20} />
                        {!collapsed && <span>レポート</span>}
                    </Link>
                    <a href="#" title="設定">
                        <Settings size={20} />
                        {!collapsed && <span>設定</span>}
                    </a>
                </nav>
                <div className="sidebar-footer">
                    <button onClick={handleLogout} className="logout-btn" title="ログアウト">
                        <LogOut size={18} />
                        {!collapsed && <span>ログアウト</span>}
                    </button>
                </div>
            </aside>

            <main className={`main-content ${collapsed ? 'expanded' : ''}`}>
                <header className="top-header">
                    <h1>{location.pathname === '/dashboard' ? 'ダッシュボード' :
                        location.pathname === '/students' ? '学生一覧' :
                            location.pathname === '/reports' ? 'レポート' :
                                location.pathname === '/attendance-register' ? '出席簿' : '管理画面'}</h1>
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
