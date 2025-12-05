import React, { useEffect, useState } from 'react';
import api from '../api';
import { AlertTriangle, CheckCircle, XCircle, Clock } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import './Dashboard.css';

function Dashboard() {
    const [attendanceData, setAttendanceData] = useState([]);
    const [summaryStats, setSummaryStats] = useState({ total: 0, present: 0, absent: 0, late: 0 });
    const [loading, setLoading] = useState(true);
    const navigate = useNavigate();

    useEffect(() => {
        fetchData();
    }, []);

    const fetchData = async () => {
        try {
            const [usersResponse, attendanceResponse] = await Promise.all([
                api.get('/admin/users'),
                api.get('/admin/attendance')
            ]);

            const students = usersResponse.data.filter(user => user.role !== 1); // Exclude admins/teachers if needed, assuming role 1 is admin
            const attendances = attendanceResponse.data;

            // Merge data
            const mergedData = students.map(student => {
                const record = attendances.find(a => a.student_id === student.student_id);
                return {
                    ...student,
                    attendance_id: record ? record.id : null,
                    status: record ? record.status : 'unrecorded',
                    timestamp: record ? record.timestamp : null,
                    recorded_by: record ? record.recorded_by : '-'
                };
            });

            setAttendanceData(mergedData);

            // Calculate summary stats based on merged data or raw attendance?
            // Usually summary is about "today's records".
            // Total students is the number of students in the class.
            setSummaryStats({
                total: students.length,
                present: attendances.filter(a => a.status === 'present').length,
                absent: attendances.filter(a => a.status === 'absent').length,
                late: attendances.filter(a => a.status === 'late').length
            });

            setLoading(false);
        } catch (error) {
            console.error('Error fetching data:', error);
            if (error.response && error.response.status === 401) {
                navigate('/login');
            }
            setLoading(false);
        }
    };

    const handleLogout = () => {
        localStorage.removeItem('token');
        navigate('/login');
    };

    const sendWarning = async (userId) => {
        try {
            await api.post('/admin/send_warning', { user_id: userId });
            alert('警告メールを送信しました！');
        } catch (error) {
            alert('警告の送信に失敗しました');
        }
    };

    const getStatusIcon = (status) => {
        switch (status) {
            case 'present': return <CheckCircle className="icon success" />;
            case 'absent': return <XCircle className="icon error" />;
            case 'late': return <Clock className="icon warning" />;
            case 'unrecorded': return <span className="icon-placeholder">-</span>;
            default: return null;
        }
    };

    const getStatusText = (status) => {
        switch (status) {
            case 'present': return '出席';
            case 'absent': return '欠席';
            case 'late': return '遅刻';
            case 'unrecorded': return '未記録';
            default: return status;
        }
    };

    if (loading) return <div className="loading">読み込み中...</div>;

    return (
        <>
            <div className="summary-cards">
                <div className="card">
                    <h3>登録学生数</h3>
                    <p className="count">{summaryStats.total}</p>
                </div>
                <div className="card present">
                    <h3>出席</h3>
                    <p className="count">{summaryStats.present}</p>
                </div>
                <div className="card absent">
                    <h3>欠席</h3>
                    <p className="count">{summaryStats.absent}</p>
                </div>
                <div className="card late">
                    <h3>遅刻</h3>
                    <p className="count">{summaryStats.late}</p>
                </div>
            </div>

            <div className="content-section">
                <h2>本日の出席簿</h2>
                <div className="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>学籍番号</th>
                                <th>氏名</th>
                                <th>ステータス</th>
                                <th>記録日時</th>
                                <th>記録者</th>
                                <th>アクション</th>
                            </tr>
                        </thead>
                        <tbody>
                            {attendanceData.map((student) => (
                                <tr key={student.id}>
                                    <td>{student.student_id}</td>
                                    <td>{student.username}</td>
                                    <td>
                                        <span className={`status-badge status-${student.status}`}>
                                            {getStatusIcon(student.status)} {getStatusText(student.status)}
                                        </span>
                                    </td>
                                    <td>{student.timestamp ? new Date(student.timestamp).toLocaleString('ja-JP') : '-'}</td>
                                    <td>{student.recorded_by}</td>
                                    <td>
                                        {student.status === 'absent' && (
                                            <button
                                                onClick={() => sendWarning(student.id)}
                                                className="warning-btn"
                                            >
                                                <AlertTriangle size={16} /> 警告
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

export default Dashboard;
