import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { UserPlus, Save, ArrowLeft } from 'lucide-react';
import api from '../api';
import './Settings.css'; // Reuse settings styles for form

function RegisterStudent() {
    const [formData, setFormData] = useState({
        student_id: '',
        username: '',
        email: ''
    });
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState(null); // { type: 'success' | 'error', text: '' }
    const navigate = useNavigate();

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setMessage(null);

        try {
            await api.post('/admin/users', formData);
            setMessage({ type: 'success', text: '学生を登録しました。初期パスワードは学籍番号です。' });
            setFormData({ student_id: '', username: '', email: '' }); // Reset form
        } catch (error) {
            console.error('Registration failed:', error);
            const errorMsg = error.response?.data?.error || '登録に失敗しました';
            setMessage({ type: 'error', text: errorMsg });
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="page-container">
            <h1 className="page-title">
                <UserPlus size={32} style={{ verticalAlign: 'middle', marginRight: '10px' }} />
                学生登録
            </h1>

            <div className="settings-container">
                <button className="secondary-btn" onClick={() => navigate('/students')} style={{ marginBottom: '1rem' }}>
                    <ArrowLeft size={16} /> 一覧に戻る
                </button>

                <div className="card settings-content" style={{ display: 'block' }}>
                    {/* Reuse settings card style */}
                    <div className="settings-section active" style={{ visibility: 'visible', opacity: 1, pointerEvents: 'auto' }}>
                        <h2>新規学生情報を入力</h2>

                        {message && (
                            <div className={`message-banner ${message.type}`}>
                                {message.text}
                            </div>
                        )}

                        <form onSubmit={handleSubmit}>
                            <div className="form-group">
                                <label>学籍番号 (ID)</label>
                                <input
                                    type="text"
                                    name="student_id"
                                    value={formData.student_id}
                                    onChange={handleChange}
                                    required
                                    placeholder="例: 20240001"
                                />
                                <div className="help-text">初期パスワードとして使用されます</div>
                            </div>

                            <div className="form-group">
                                <label>氏名</label>
                                <input
                                    type="text"
                                    name="username"
                                    value={formData.username}
                                    onChange={handleChange}
                                    required
                                    placeholder="例: 山田 太郎"
                                />
                            </div>

                            <div className="form-group">
                                <label>メールアドレス</label>
                                <input
                                    type="email"
                                    name="email"
                                    value={formData.email}
                                    onChange={handleChange}
                                    required
                                    placeholder="例: student@school.edu"
                                />
                            </div>

                            <div style={{ marginTop: '2rem' }}>
                                <button type="submit" className="primary-btn" disabled={loading}>
                                    <Save size={18} />
                                    {loading ? '登録中...' : '登録する'}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default RegisterStudent;
