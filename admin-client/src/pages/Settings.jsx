import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Save, Download, Key, AlertTriangle, Monitor } from 'lucide-react';
import './Settings.css';

const Settings = () => {
    const [activeTab, setActiveTab] = useState('system');
    const [message, setMessage] = useState({ type: '', text: '' });

    // System Settings State
    const [settings, setSettings] = useState({
        warning_threshold: '20'
    });

    // Password Change State
    const [passwordData, setPasswordData] = useState({
        current_password: '',
        new_password: '',
        confirm_password: ''
    });

    useEffect(() => {
        fetchSettings();
    }, []);

    const fetchSettings = async () => {
        try {
            const token = localStorage.getItem('token');
            const response = await axios.get('/api/admin/system_settings', {
                headers: { Authorization: `Bearer ${token}` }
            });
            setSettings(response.data);
        } catch (error) {
            console.error('Failed to fetch settings', error);
        }
    };

    const handleSystemSettingChange = (e) => {
        setSettings({ ...settings, [e.target.name]: e.target.value });
    };

    const saveSystemSettings = async (e) => {
        e.preventDefault();
        setMessage({ type: '', text: '' });

        try {
            const token = localStorage.getItem('token');
            await axios.post('/api/admin/system_settings', settings, {
                headers: { Authorization: `Bearer ${token}` }
            });
            setMessage({ type: 'success', text: 'システム設定を保存しました' });
        } catch (error) {
            setMessage({ type: 'error', text: '設定の保存に失敗しました' });
        }
    };

    const exportCsv = async () => {
        try {
            const token = localStorage.getItem('token');
            const response = await axios.get('/api/admin/export_csv', {
                headers: { Authorization: `Bearer ${token}` },
                responseType: 'blob', // Important for file download
            });

            // Create download link
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', 'attendance_data.csv');
            document.body.appendChild(link);
            link.click();
            link.remove();

            setMessage({ type: 'success', text: 'CSVのエクスポートを開始しました' });
        } catch (error) {
            setMessage({ type: 'error', text: 'エクスポートに失敗しました' });
        }
    };

    const handlePasswordChange = (e) => {
        setPasswordData({ ...passwordData, [e.target.name]: e.target.value });
    };

    const changePassword = async (e) => {
        e.preventDefault();
        setMessage({ type: '', text: '' });

        if (passwordData.new_password !== passwordData.confirm_password) {
            setMessage({ type: 'error', text: '新しいパスワードが一致しません' });
            return;
        }

        try {
            const token = localStorage.getItem('token');
            await axios.post('/api/admin/change_password', {
                current_password: passwordData.current_password,
                new_password: passwordData.new_password
            }, {
                headers: { Authorization: `Bearer ${token}` }
            });

            setMessage({ type: 'success', text: 'パスワードを変更しました' });
            setPasswordData({ current_password: '', new_password: '', confirm_password: '' });
        } catch (error) {
            setMessage({ type: 'error', text: error.response?.data?.error || 'パスワード変更に失敗しました' });
        }
    };

    return (
        <div className="settings-container">
            <h1 className="page-title">設定</h1>

            {message.text && (
                <div className={`message-banner ${message.type}`}>
                    {message.type === 'success' ? <CheckCircle size={20} /> : <AlertTriangle size={20} />}
                    <span>{message.text}</span>
                </div>
            )}

            <div className="settings-layout">
                <div className="settings-sidebar">
                    <button
                        className={`tab-btn ${activeTab === 'system' ? 'active' : ''}`}
                        onClick={() => setActiveTab('system')}
                    >
                        <Monitor size={18} />
                        システム設定
                    </button>
                    <button
                        className={`tab-btn ${activeTab === 'data' ? 'active' : ''}`}
                        onClick={() => setActiveTab('data')}
                    >
                        <Download size={18} />
                        データ管理
                    </button>
                    <button
                        className={`tab-btn ${activeTab === 'account' ? 'active' : ''}`}
                        onClick={() => setActiveTab('account')}
                    >
                        <Key size={18} />
                        アカウント設定
                    </button>
                </div>

                <div className="settings-content card">
                    <div className={`settings-section ${activeTab === 'system' ? 'active' : ''}`}>
                        <h2>システム設定</h2>
                        <form onSubmit={saveSystemSettings}>
                            <div className="form-group">
                                <label>欠席警告ライン（回数）</label>
                                <input
                                    type="number"
                                    name="warning_threshold"
                                    value={settings.warning_threshold}
                                    onChange={handleSystemSettingChange}
                                    min="1"
                                />
                                <p className="help-text">この回数以上の欠席がある学生は「警告対象」として表示されます。</p>
                            </div>
                            <button type="submit" className="primary-btn">
                                <Save size={18} />
                                設定を保存
                            </button>
                        </form>
                    </div>

                    <div className={`settings-section ${activeTab === 'data' ? 'active' : ''}`}>
                        <h2>データ管理</h2>
                        <div className="data-actions">
                            <div className="action-item">
                                <h3>CSVエクスポート</h3>
                                <p>全学生の出席データをCSV形式でダウンロードします。</p>
                                <button onClick={exportCsv} className="secondary-btn">
                                    <Download size={18} />
                                    ダウンロード
                                </button>
                            </div>
                        </div>
                    </div>

                    <div className={`settings-section ${activeTab === 'account' ? 'active' : ''}`}>
                        <h2>パスワード変更</h2>
                        <form onSubmit={changePassword}>
                            <div className="form-group">
                                <label>現在のパスワード</label>
                                <input
                                    type="password"
                                    name="current_password"
                                    value={passwordData.current_password}
                                    onChange={handlePasswordChange}
                                    required
                                />
                            </div>
                            <div className="form-group">
                                <label>新しいパスワード</label>
                                <input
                                    type="password"
                                    name="new_password"
                                    value={passwordData.new_password}
                                    onChange={handlePasswordChange}
                                    required
                                    minLength="6"
                                />
                            </div>
                            <div className="form-group">
                                <label>新しいパスワード（確認）</label>
                                <input
                                    type="password"
                                    name="confirm_password"
                                    value={passwordData.confirm_password}
                                    onChange={handlePasswordChange}
                                    required
                                    minLength="6"
                                />
                            </div>
                            <button type="submit" className="primary-btn">
                                <Key size={18} />
                                パスワードを変更
                            </button>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    );
};

// Simple Icon component for message banner (since CheckCircle wasn't imported initially)
const CheckCircle = ({ size }) => (
    <svg xmlns="http://www.w3.org/2000/svg" width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="lucide lucide-check-circle"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" /><polyline points="22 4 12 14.01 9 11.01" /></svg>
);

export default Settings;
