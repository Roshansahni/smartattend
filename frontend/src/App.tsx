import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './context/AuthContext';
import LoginPage from './pages/auth/LoginPage';
import ForgotPasswordPage from './pages/auth/ForgotPasswordPage';
import DashboardLayout from './components/shared/DashboardLayout';

// Student Pages
import StudentDashboard from './pages/student/StudentDashboard';
import ScanQRPage from './pages/student/ScanQRPage';
import AttendanceHistoryPage from './pages/student/AttendanceHistoryPage';
import AttendanceCalendarPage from './pages/student/AttendanceCalendarPage';
import TimetablePage from './pages/student/TimetablePage';
import LeaveApplicationPage from './pages/student/LeaveApplicationPage';
import DisputePage from './pages/student/DisputePage';
import NotificationsPage from './pages/student/NotificationsPage';
import StudentProfilePage from './pages/student/StudentProfilePage';

// Faculty Pages
import FacultyDashboard from './pages/faculty/FacultyDashboard';
import AttendanceSessionPage from './pages/faculty/AttendanceSessionPage';
import ManualAttendancePage from './pages/faculty/ManualAttendancePage';
import LeaveApprovalPage from './pages/faculty/LeaveApprovalPage';
import FacultyReportsPage from './pages/faculty/FacultyReportsPage';

// Admin & Super Admin Pages
import AdminDashboard from './pages/admin/AdminDashboard';
import StudentsPage from './pages/admin/StudentsPage';
import FacultyPage from './pages/admin/FacultyPage';
import DepartmentPage from './pages/admin/DepartmentPage';
import TimetableManagementPage from './pages/admin/TimetableManagementPage';
import SystemConfigPage from './pages/admin/SystemConfigPage';
import AuditLogsPage from './pages/admin/AuditLogsPage';
import SuperAdminDashboard from './pages/admin/SuperAdminDashboard';

function ProtectedRoute({ children, roles }: { children: React.ReactNode; roles?: string[] }) {
  const { isAuthenticated, role, isLoading } = useAuth();
  if (isLoading) return <div className="h-screen flex items-center justify-center font-semibold text-slate-500">Loading SmartAttend ERP...</div>;
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  if (roles && role && !roles.includes(role)) return <Navigate to="/" replace />;
  return <>{children}</>;
}

function RoleHome() {
  const { role } = useAuth();
  if (role === 'student') return <Navigate to="/student/dashboard" replace />;
  if (role === 'faculty') return <Navigate to="/faculty/dashboard" replace />;
  if (role === 'super_admin') return <Navigate to="/superadmin/dashboard" replace />;
  return <Navigate to="/admin/dashboard" replace />;
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/forgot-password" element={<ForgotPasswordPage />} />
      <Route path="/" element={<ProtectedRoute><RoleHome /></ProtectedRoute>} />

      {/* Student ERP Portal */}
      <Route path="/student" element={<ProtectedRoute roles={['student']}><DashboardLayout /></ProtectedRoute>}>
        <Route path="dashboard" element={<StudentDashboard />} />
        <Route path="scan" element={<ScanQRPage />} />
        <Route path="attendance" element={<AttendanceHistoryPage />} />
        <Route path="calendar" element={<AttendanceCalendarPage />} />
        <Route path="timetable" element={<TimetablePage />} />
        <Route path="leave" element={<LeaveApplicationPage />} />
        <Route path="dispute" element={<DisputePage />} />
        <Route path="notifications" element={<NotificationsPage />} />
        <Route path="profile" element={<StudentProfilePage />} />
      </Route>

      {/* Faculty ERP Portal */}
      <Route path="/faculty" element={<ProtectedRoute roles={['faculty']}><DashboardLayout /></ProtectedRoute>}>
        <Route path="dashboard" element={<FacultyDashboard />} />
        <Route path="session/:sessionId" element={<AttendanceSessionPage />} />
        <Route path="manual" element={<ManualAttendancePage />} />
        <Route path="leaves" element={<LeaveApprovalPage />} />
        <Route path="reports" element={<FacultyReportsPage />} />
        <Route path="profile" element={<StudentProfilePage />} />
      </Route>

      {/* Admin ERP Portal */}
      <Route path="/admin" element={<ProtectedRoute roles={['admin', 'super_admin']}><DashboardLayout /></ProtectedRoute>}>
        <Route path="dashboard" element={<AdminDashboard />} />
        <Route path="students" element={<StudentsPage />} />
        <Route path="faculty" element={<FacultyPage />} />
        <Route path="departments" element={<DepartmentPage />} />
        <Route path="timetable" element={<TimetableManagementPage />} />
        <Route path="config" element={<SystemConfigPage />} />
        <Route path="audit" element={<AuditLogsPage />} />
      </Route>

      {/* Super Admin Enterprise Portal */}
      <Route path="/superadmin" element={<ProtectedRoute roles={['super_admin']}><DashboardLayout /></ProtectedRoute>}>
        <Route path="dashboard" element={<SuperAdminDashboard />} />
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
