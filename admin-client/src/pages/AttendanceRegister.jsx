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
                            <th style={{ position: 'sticky', left: 0, background: '#f8f9fa', zIndex: 1, minWidth: '100px' }}>学籍番号</th>
                            <th style={{ position: 'sticky', left: '100px', background: '#f8f9fa', zIndex: 1, minWidth: '150px', whiteSpace: 'nowrap' }}>氏名</th>
                            <th>出席</th>
                            <th>遅刻</th>
                            <th>欠席</th>
                            {daysArray.map(day => (
                                <th key={day} style={{ minWidth: '50px', textAlign: 'center' }}>{day}</th>
                            ))}
                        </tr>
                    </thead>
                    <tbody>
                        {data?.students.map((student) => (
                            <tr key={student.id}>
                                <td style={{ position: 'sticky', left: 0, background: 'white', zIndex: 1 }}>{student.student_id}</td>
                                <td style={{ position: 'sticky', left: '100px', background: 'white', zIndex: 1, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', maxWidth: '150px' }}>{student.username}</td>
                                <td>{student.summary.present}</td>
                                <td>{student.summary.late}</td>
                                <td style={{ color: student.summary.absent >= 20 ? 'red' : 'inherit', fontWeight: student.summary.absent >= 20 ? 'bold' : 'normal' }}>
                                    {student.summary.absent}
                                </td>
                                {daysArray.map(day => {
                                    // Parse daily status if it's not a simple string anymore, or we might need to fetch detailed data.
                                    // Wait, the current API `get_monthly_attendance` returns `daily_status[day] = status_string`.
                                    // We need it to return valid data (e.g. Map<Period, Status> or Array of records).
                                    // Currently `daily_status` in backend just overwrites: `daily_status[day] = att.status`.
                                    // We need to update Backend `get_monthly_attendance` first to return DETAILED daily status!
                                    // Ah, I missed that step in the plan. The current backend logic overwrites the status.
                                    // I should update the Frontend assuming the Backend will return a map or list, 
                                    // AND I need to update the Backend `get_monthly_attendance` to return details.

                                    // Let's assume Backend returns an object for each day: { 1: 'present', 3: 'absent' } etc.
                                    // Or simplified: Just the "Best Status" string?
                                    // No, to implement "1:出" or "2:出", we need to know the Period.

                                    // I must update the Backend first or simultaneously.
                                    // For now, I'll update this to handle the EXPECTED data structure:
                                    // daily_status[day] = { period: status, ... } OR Array.

                                    // Let's update Backend to return: daily_status[day] = [ { period: 1, status: 'present' }, ... ]

                                    const dayRecords = student.daily_status[day]; // Expecting Array or Object
                                    let displayText = '-';
                                    let displayColor = 'transparent';

                                    if (Array.isArray(dayRecords) && dayRecords.length > 0) {
                                        // Priority: Present/Late > Absent
                                        // Sort by priority? Or find first.
                                        const presentOrLate = dayRecords.find(r => r.status === 'present' || r.status === 'late');
                                        const absent = dayRecords.find(r => r.status === 'absent');

                                        const targetRecord = presentOrLate || absent || dayRecords[0];

                                        if (targetRecord) {
                                            const statusMap = { 'present': '出', 'late': '遅', 'absent': '欠' };
                                            displayText = `${targetRecord.period}:${statusMap[targetRecord.status] || '-'}`;

                                            // Color
                                            if (targetRecord.status === 'present') displayColor = '#c6f6d5';
                                            else if (targetRecord.status === 'late') displayColor = '#fefcbf';
                                            else if (targetRecord.status === 'absent') displayColor = '#fed7d7';
                                        }
                                    } else if (typeof dayRecords === 'string') {
                                        // Fallback for old API response (just status string)
                                        const statusMap = { 'present': '出', 'late': '遅', 'absent': '欠' };
                                        displayText = statusMap[dayRecords] || '-';
                                        if (dayRecords === 'present') displayColor = '#c6f6d5';
                                        else if (dayRecords === 'late') displayColor = '#fefcbf';
                                        else if (dayRecords === 'absent') displayColor = '#fed7d7';
                                    }

                                    return (
                                        <td key={day} style={{
                                            backgroundColor: displayColor,
                                            textAlign: 'center',
                                            padding: '4px',
                                            fontSize: '0.85rem'
                                        }}>
                                            {displayText}
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
