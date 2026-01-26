import React, { useEffect, useState } from 'react';
import api from '../api';
import { AlertTriangle, CheckCircle, XCircle, Clock, Users, UserCheck, UserX } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import './Dashboard.css';

function Dashboard() {
    const [stats, setStats] = useState({
        date: '',
        total_students: 0,
        present: 0,
        late: 0,
        absent: 0
    });
    const [loading, setLoading] = useState(true);
    const navigate = useNavigate();

    useEffect(() => {
        fetchStats();
    }, []);

    const fetchStats = async () => {
        try {
            const response = await api.get('/admin/daily_stats');
            setStats(response.data);
            setLoading(false);
        } catch (error) {
            console.error('Error fetching stats:', error);
            if (error.response && error.response.status === 401) {
                navigate('/login');
            }
            setLoading(false);
        }
    };

    if (loading) return <div className="loading">読み込み中...</div>;

    // Calculate percentages based on total students
    const total = stats.total_students || 1; // Avoid division by zero
    const presentRate = Math.round((stats.present / total) * 100);

    // Calculate absent count
    // Use 'arrived_count' from API if available to calculate accurate "Not at School" count.
    // Fallback to previous logic if API hasn't updated yet.
    const arrived = stats.arrived_count !== undefined ? stats.arrived_count : (stats.present + stats.late);
    const calculatedAbsent = Math.max(0, stats.total_students - arrived);

    return (
        <>
            <div className="summary-cards">
                <div className="card total">
                    <h3><Users size={20} /> 学生総数</h3>
                    <p className="count">{stats.total_students}名</p>
                    <p className="label">登録済み学生</p>
                </div>
                <div className="card present">
                    <h3><UserCheck size={20} /> 本日の出席</h3>
                    <p className="count">{stats.present}名</p>
                    <p className="label">出席率: {presentRate}%</p>
                </div>
                <div className="card late">
                    <h3><Clock size={20} /> 本日の遅刻</h3>
                    <p className="count">{stats.late}名</p>
                    <p className="label">遅刻者数</p>
                </div>
                <div className="card absent">
                    <h3><UserX size={20} /> 本日の欠席</h3>
                    <p className="count">{calculatedAbsent}名</p>
                    <p className="label">欠席者数</p>
                </div>
            </div>

            <div className="content-section">
                <h2>本日の出欠状況 ({stats.date})</h2>
                <p>※ 詳細な月次データはサイドメニューの「出席簿」から確認してください。</p>
            </div>
        </>
    );
}

export default Dashboard;
