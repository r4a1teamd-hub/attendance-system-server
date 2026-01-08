import React, { useEffect, useState } from 'react';
import api from '../api';
import { useNavigate } from 'react-router-dom';
import './Dashboard.css'; // Reuse dashboard styles

function Students() {
    const [students, setStudents] = useState([]);
    const [loading, setLoading] = useState(true);
    const navigate = useNavigate();

    useEffect(() => {
        fetchStudents();
    }, []);

    const fetchStudents = async () => {
        try {
            const response = await api.get('/admin/users');
            // Filter out teachers (role 1)
            const studentOnly = response.data.filter(user => user.role !== 1);
            setStudents(studentOnly);
            setLoading(false);
        } catch (error) {
            console.error('Error fetching students:', error);
            if (error.response && error.response.status === 401) {
                navigate('/login');
            }
            setLoading(false);
        }
    };

    if (loading) return <div className="loading">読み込み中...</div>;

    return (
        <div className="content-section">
            <h2>登録学生一覧</h2>
            <div className="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>学籍番号</th>
                            <th>氏名</th>
                            <th>メールアドレス</th>
                        </tr>
                    </thead>
                    <tbody>
                        {students.map((student) => (
                            <tr key={student.id}>
                                <td>#{student.id}</td>
                                <td>{student.student_id}</td>
                                <td>{student.username}</td>
                                <td>{student.email}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}

export default Students;
