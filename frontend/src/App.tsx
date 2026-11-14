import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './context/AuthContext';
import LoginPage from './pages/auth/LoginPage';
import ForgotPasswordPage from './pages/auth/ForgotPasswordPage';
import StudentDashboard from './pages/student/StudentDashboard';
import ScanQRPage from './pages/student/ScanQRPage';
import AttendanceHistoryPage from './pages/student/AttendanceHistoryPage';
import FacultyDashboard from './pages/faculty/FacultyDashboard';
import AttendanceSessionPage from './pages/faculty/AttendanceSessionPage';
import AdminDashboard from './pages/admin/AdminDashboard';
import StudentsPage from './pages/admin/StudentsPage';
import FacultyPage from './pages/admin/FacultyPage';
import DashboardLayout from './components/shared/DashboardLayout';

function ProtectedRoute({ children, roles }: { children: React.ReactNode; roles?: string[] }) {
  const { isAuthenticated, role, isLoading } = useAuth();
  if (isLoading) return <div className="h-screen flex items-center justify-center">Loading SmartAttend...</div>;
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  if (roles && role && !roles.includes(role)) return <Navigate to="/" replace />;
  return <>{children}</>;
}

function RoleHome() {
  const { role } = useAuth();
  if (role === 'student') return <Navigate to="/student/dashboard" replace />;
  if (role === 'faculty') return <Navigate to="/faculty/dashboard" replace />;
  return <Navigate to="/admin/dashboard" replace />;
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/forgot-password" element={<ForgotPasswordPage />} />
      <Route path="/" element={<ProtectedRoute><RoleHome /></ProtectedRoute>} />

      <Route path="/student" element={<ProtectedRoute roles={['student']}><DashboardLayout /></ProtectedRoute>}>
        <Route path="dashboard" element={<StudentDashboard />} />
        <Route path="scan" element={<ScanQRPage />} />
        <Route path="attendance" element={<AttendanceHistoryPage />} />
      </Route>

      <Route path="/faculty" element={<ProtectedRoute roles={['faculty']}><DashboardLayout /></ProtectedRoute>}>
        <Route path="dashboard" element={<FacultyDashboard />} />
        <Route path="session/:sessionId" element={<AttendanceSessionPage />} />
      </Route>

      <Route path="/admin" element={<ProtectedRoute roles={['admin', 'super_admin']}><DashboardLayout /></ProtectedRoute>}>
        <Route path="dashboard" element={<AdminDashboard />} />
        <Route path="students" element={<StudentsPage />} />
        <Route path="faculty" element={<FacultyPage />} />
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
