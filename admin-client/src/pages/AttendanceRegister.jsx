import React, { useEffect, useState } from 'react';
import api from '../api';
import './Dashboard.css'; // Reuse dashboard styles for table

function AttendanceRegister() {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [year, setYear] = useState(new Date().getFullYear());
    const [month, setMonth] = useState(new Date().getMonth() + 1);

    useEffect(() => {
        fetchMonthlyData();
    }, [year, month]);

    const fetchMonthlyData = async () => {
        setLoading(true);
        try {
            const response = await api.get(`/admin/monthly_attendance?year=${year}&month=${month}`);
            setData(response.data);
        } catch (error) {
            console.error('Error fetching monthly attendance:', error);
            alert('データの取得に失敗しました。');
        } finally {
            setLoading(false);
        }
    };

    const handleMonthChange = (e) => {
        const [y, m] = e.target.value.split('-');
        setYear(parseInt(y));
        setMonth(parseInt(m));
    };

    // Helper to get days in month
    const getDaysInMonth = (y, m) => {
        return new Date(y, m, 0).getDate();
    };

    if (loading && !data) return <div className="loading">読み込み中...</div>;

    const daysInMonth = getDaysInMonth(year, month);
    const daysArray = Array.from({ length: daysInMonth }, (_, i) => i + 1);

    const getStatusColor = (status) => {
        switch (status) {
            case 'present': return '#c6f6d5'; // Green
            case 'late': return '#fefcbf'; // Yellow
            case 'absent': return '#fed7d7'; // Red
            default: return 'transparent';
        }
    };

    const getStatusText = (status) => {
        switch (status) {
            case 'present': return '出';
            case 'late': return '遅';
            case 'absent': return '欠';
            default: return '-';
        }
    };

    return (
        <div className="content-section">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                <h2>月次出席簿</h2>
                <input
                    type="month"
                    value={`${year}-${String(month).padStart(2, '0')}`}
                    onChange={handleMonthChange}
                    style={{ padding: '0.5rem', borderRadius: '4px', border: '1px solid #ddd' }}
                />
            </div>

            <div className="table-container" style={{ overflowX: 'auto' }}>
                <table style={{ minWidth: '100%' }}>
                    <thead>
                        <tr>
                            <th style={{ position: 'sticky', left: 0, background: '#f8f9fa', zIndex: 1 }}>学籍番号</th>
                            <th style={{ position: 'sticky', left: '100px', background: '#f8f9fa', zIndex: 1 }}>氏名</th>
                            <th>出席</th>
                            <th>遅刻</th>
                            <th>欠席</th>
                            {daysArray.map(day => (
                                <th key={day} style={{ minWidth: '30px', textAlign: 'center' }}>{day}</th>
                            ))}
                        </tr>
                    </thead>
                    <tbody>
                        {data?.students.map((student) => (
                            <tr key={student.id}>
                                <td style={{ position: 'sticky', left: 0, background: 'white', zIndex: 1 }}>{student.student_id}</td>
                                <td style={{ position: 'sticky', left: '100px', background: 'white', zIndex: 1 }}>{student.username}</td>
                                <td>{student.summary.present}</td>
                                <td>{student.summary.late}</td>
                                <td style={{ color: student.summary.absent >= 20 ? 'red' : 'inherit', fontWeight: student.summary.absent >= 20 ? 'bold' : 'normal' }}>
                                    {student.summary.absent}
                                </td>
                                {daysArray.map(day => {
                                    const status = student.daily_status[day];
                                    return (
                                        <td key={day} style={{
                                            backgroundColor: getStatusColor(status),
                                            textAlign: 'center',
                                            padding: '4px'
                                        }}>
                                            {getStatusText(status)}
                                        </td>
                                    );
                                })}
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}

export default AttendanceRegister;
