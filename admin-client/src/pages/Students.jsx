import React, { useEffect, useState } from 'react';
import api from '../api';
import { useNavigate } from 'react-router-dom';
import { RotateCcw, Trash2 } from 'lucide-react';
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

    const handleResetPassword = async (userId, studentId) => {
        if (!window.confirm(`${studentId} のパスワードを初期化（学籍番号に変更）しますか？\n\n※ユーザーは次回ログイン時にパスワード変更が求められます。`)) {
            return;
        }

        try {
            await api.post('/admin/reset_password', { user_id: userId });
            alert('パスワードを初期化しました。');
        } catch (error) {
            console.error('Reset password failed:', error);
            alert('初期化に失敗しました。');
        }
    };

    const handleDeleteUser = async (userId, studentId) => {
        if (!window.confirm(`${studentId} を本当に削除しますか？\n\n※このユーザーの出席データも全て削除されます。\n※この操作は取り消せません。`)) {
            return;
        }

        try {
            await api.delete(`/admin/users/${userId}`);
            alert('ユーザーを削除しました。');
            fetchStudents(); // Refresh list
        } catch (error) {
            console.error('Delete user failed:', error);
            alert('削除に失敗しました。');
        }
    };

    if (loading) return <div className="loading">読み込み中...</div>;

    return (
        <div className="content-section">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                <h2 style={{ margin: 0 }}>登録学生一覧</h2>
                <button
                    className="primary-btn"
                    onClick={() => navigate('/register-student')}
                    style={{ padding: '8px 16px' }}
                >
                    + 新規登録
                </button>
            </div>
            <div className="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>学籍番号</th>
                            <th>氏名</th>
                            <th>メールアドレス</th>
                            <th>操作</th>
                        </tr>
                    </thead>
                    <tbody>
                        {students.map((student) => (
                            <tr key={student.id}>
                                <td>#{student.id}</td>
                                <td>{student.student_id}</td>
                                <td>{student.username}</td>
                                <td>{student.email}</td>
                                <td>
                                    <button
                                        onClick={() => handleResetPassword(student.id, student.student_id)}
                                        className="warning-btn"
                                        title="パスワードを学籍番号に初期化"
                                    >
                                        <RotateCcw size={16} style={{ marginRight: '4px' }} /> 初期化
                                    </button>
                                    <button
                                        onClick={() => handleDeleteUser(student.id, student.student_id)}
                                        className="delete-btn"
                                        title="ユーザーを削除"
                                        style={{ marginLeft: '8px', backgroundColor: '#e74c3c', color: 'white', border: 'none', padding: '5px 10px', borderRadius: '4px', cursor: 'pointer' }}
                                    >
                                        <Trash2 size={16} style={{ marginRight: '4px' }} /> 削除
                                    </button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}

export default Students;
