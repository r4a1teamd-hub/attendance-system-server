import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Students from './pages/Students';
import Reports from './pages/Reports';
import AttendanceRegister from './pages/AttendanceRegister';
import RegisterStudent from './pages/RegisterStudent';
import Settings from './pages/Settings';
import Layout from './components/Layout';
import './App.css';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route element={<Layout />}>
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/students" element={<Students />} />
          <Route path="/reports" element={<Reports />} />
          <Route path="/attendance-register" element={<AttendanceRegister />} />
          <Route path="/register-student" element={<RegisterStudent />} />
          <Route path="/settings" element={<Settings />} />
        </Route>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </Router>
  );
}

export default App;
