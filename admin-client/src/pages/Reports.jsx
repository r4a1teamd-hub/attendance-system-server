import React, { useEffect, useState } from 'react';
import api from '../api';
import { AlertTriangle, Mail } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import './Dashboard.css'; // Reuse dashboard styles

function Reports() {
    const [stats, setStats] = useState([]);
    const [loading, setLoading] = useState(true);
    const navigate = useNavigate();

    useEffect(() => {
        fetchStats();
    }, []);

    const fetchStats = async () => {
        try {
            const response = await api.get('/admin/stats');
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

    const sendWarning = async (userId) => {
        if (!window.confirm('この学生に警告メールを送信しますか？')) return;

        try {
            await api.post('/admin/send_warning', { user_id: userId });
            alert('警告メールを送信しました！');
        } catch (error) {
            console.error('Error sending warning:', error);
            alert('警告の送信に失敗しました。サーバーログを確認してください。');
        }
    };

    if (loading) return <div className="loading">読み込み中...</div>;

    // Filter students with high warning level (absent >= 20)
    const warningStudents = stats.filter(s => s.warning_level === 'high');

    return (
        <>
            {warningStudents.length > 0 && (
                <div className="summary-cards" style={{ marginBottom: '2rem' }}>
                    <div className="card absent" style={{ gridColumn: '1 / -1' }}>
                        <h3 style={{ color: '#c53030', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                            <AlertTriangle size={20} /> 警告対象学生 (欠席20回以上)
                        </h3>
                        <p className="count">{warningStudents.length}名</p>
                    </div>
                </div>
            )}

            <div className="content-section">
                <h2>出席統計レポート</h2>
                <div className="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>学籍番号</th>
                                <th>氏名</th>
                                <th>メールアドレス</th>
                                <th>出席</th>
                                <th>遅刻</th>
                                <th>欠席</th>
                                <th>状態</th>
                                <th>アクション</th>
                            </tr>
                        </thead>
                        <tbody>
                            {stats.map((student) => (
                                <tr key={student.id} style={student.warning_level === 'high' ? { backgroundColor: '#fff5f5' } : {}}>
                                    <td>{student.student_id}</td>
                                    <td>{student.username}</td>
                                    <td>{student.email}</td>
                                    <td>{student.present}</td>
                                    <td>{student.late}</td>
                                    <td style={student.absent >= 20 ? { color: '#c53030', fontWeight: 'bold' } : {}}>
                                        {student.absent}
                                    </td>
                                    <td>
                                        {student.warning_level === 'high' ? (
                                            <span className="status-badge status-absent">
                                                <AlertTriangle size={14} style={{ marginRight: '4px' }} /> 警告対象
                                            </span>
                                        ) : (
                                            <span className="status-badge status-present">正常</span>
                                        )}
                                    </td>
                                    <td>
                                        {student.warning_level === 'high' && (
                                            <button
                                                onClick={() => sendWarning(student.id)}
                                                className="warning-btn"
                                            >
                                                <Mail size={16} /> メール送信
                                            </button>
                                        )}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </>
    );
}

export default Reports;
