import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api';
import './Login.css';

function Login() {
    const [studentId, setStudentId] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const navigate = useNavigate();

    const handleLogin = async (e) => {
        e.preventDefault();
        setError('');
        try {
            const response = await api.post('/login', { student_id: studentId, password });

            const user = response.data.user;

            // Check if user has admin role (role === 1)
            if (user && user.role === 1) {
                localStorage.setItem('token', response.data.token);
                navigate('/dashboard');
            } else {
                setError('管理者アカウントのみログイン可能です');
            }
        } catch (err) {
            console.error('Login error:', err);
            setError('認証情報が無効です');
        }
    };

    return (
        <div className="login-page">
            <div className="login-intro">
                <div className="intro-content">
                    <h1>Attenix</h1>
                    <p className="subtitle">Attendance Management System</p>
                    <div className="features">
                        <div className="feature-item">
                            <span className="icon">✓</span>
                            <span>リアルタイムな出席状況の把握</span>
                        </div>
                        <div className="feature-item">
                            <span className="icon">✓</span>
                            <span>月次レポートの自動集計</span>
                        </div>
                        <div className="feature-item">
                            <span className="icon">✓</span>
                            <span>学生への自動警告通知機能</span>
                        </div>
                    </div>
                </div>
                <div className="intro-footer">
                    <p>&copy; 2026 Domain Φ. All rights reserved.</p>
                </div>
            </div>

            <div className="login-form-section">
                <div className="login-wrapper">
                    <form onSubmit={handleLogin} className="login-form">
                        <div className="form-header">
                            <h2>管理者ログイン</h2>
                            <p>アカウント情報を入力して続行してください</p>
                        </div>

                        {error && <p className="error">{error}</p>}

                        <div className="form-group">
                            <label>教員ID</label>
                            <input
                                type="text"
                                placeholder="例: 12345678"
                                value={studentId}
                                onChange={(e) => setStudentId(e.target.value)}
                            />
                        </div>

                        <div className="form-group">
                            <label>パスワード</label>
                            <input
                                type="password"
                                placeholder="••••••••"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                            />
                        </div>

                        <button type="submit">ログイン</button>
                    </form>
                </div>
            </div>
        </div>
    );

}

export default Login;
