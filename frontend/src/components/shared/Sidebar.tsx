import React from 'react';
import { NavLink } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { useTheme } from '@/context/ThemeContext';
import {
  LayoutDashboard, QrCode, ClipboardList, Calendar, Clock,
  FileText, Bell, User, CheckSquare, BarChart3, Users,
  GraduationCap, Building2, Sliders, ShieldAlert, Sun, Moon, LogOut,
  HelpCircle, Globe
} from 'lucide-react';
import { cn } from '@/utils/cn';

export default function Sidebar() {
  const { role, user, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();

  const studentNav = [
    { to: '/student/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
    { to: '/student/scan', icon: QrCode, label: 'Scan Live QR' },
    { to: '/student/attendance', icon: ClipboardList, label: 'Attendance History' },
    { to: '/student/calendar', icon: Calendar, label: 'Attendance Calendar' },
    { to: '/student/timetable', icon: Clock, label: 'Class Timetable' },
    { to: '/student/leave', icon: FileText, label: 'Leave Application' },
    { to: '/student/dispute', icon: HelpCircle, label: 'Attendance Dispute' },
    { to: '/student/notifications', icon: Bell, label: 'Notifications' },
    { to: '/student/profile', icon: User, label: 'My Profile' },
  ];

  const facultyNav = [
    { to: '/faculty/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
    { to: '/faculty/session/bc8844a8-25a0-42e8-ad27-153ed7a89676', icon: QrCode, label: 'Generate Dynamic QR' },
    { to: '/faculty/manual', icon: CheckSquare, label: 'Manual Attendance' },
    { to: '/faculty/leaves', icon: FileText, label: 'Leave Approvals' },
    { to: '/faculty/reports', icon: BarChart3, label: 'Attendance Reports' },
    { to: '/faculty/profile', icon: User, label: 'My Profile' },
  ];

  const adminNav = [
    { to: '/admin/dashboard', icon: LayoutDashboard, label: 'Admin Command' },
    { to: '/admin/students', icon: GraduationCap, label: 'Student Directory' },
    { to: '/admin/faculty', icon: Users, label: 'Faculty Directory' },
    { to: '/admin/departments', icon: Building2, label: 'Departments' },
    { to: '/admin/timetable', icon: Clock, label: 'Timetable Scheduling' },
    { to: '/admin/config', icon: Sliders, label: 'System Configuration' },
    { to: '/admin/audit', icon: ShieldAlert, label: 'Security Audit Logs' },
  ];

  const superAdminNav = [
    { to: '/superadmin/dashboard', icon: Globe, label: 'Multi-Campus ERP' },
    { to: '/admin/dashboard', icon: LayoutDashboard, label: 'College Analytics' },
    { to: '/admin/students', icon: GraduationCap, label: 'All Students' },
    { to: '/admin/faculty', icon: Users, label: 'All Faculty' },
    { to: '/admin/config', icon: Sliders, label: 'Enterprise Security' },
    { to: '/admin/audit', icon: ShieldAlert, label: 'Audit Trail' },
  ];

  const navItems =
    role === 'student'
      ? studentNav
      : role === 'faculty'
      ? facultyNav
      : role === 'super_admin'
      ? superAdminNav
      : adminNav;

  return (
    <div className="w-64 bg-white dark:bg-slate-800 border-r border-slate-200 dark:border-slate-700 flex flex-col h-full shrink-0">
      {/* Brand Header */}
      <div className="p-5 border-b border-slate-100 dark:border-slate-700 flex items-center gap-3">
        <div className="h-9 w-9 bg-primary-600 rounded-xl flex items-center justify-center text-white shadow-sm">
          <QrCode className="h-5 w-5" />
        </div>
        <div>
          <span className="font-bold text-slate-900 dark:text-white text-base block leading-none">SmartAttend</span>
          <span className="text-[10px] text-primary-600 font-semibold uppercase tracking-wider mt-1 block">University ERP</span>
        </div>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
        {navItems.map(item => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) => cn(
              'flex items-center gap-3 px-3 py-2 rounded-lg text-xs font-semibold transition-all',
              isActive
                ? 'bg-primary-600 text-white shadow-sm'
                : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-700 hover:text-slate-900 dark:hover:text-white'
            )}
          >
            <item.icon className="h-4 w-4 shrink-0" />
            <span className="truncate">{item.label}</span>
          </NavLink>
        ))}
      </nav>

      {/* User Footer */}
      <div className="p-3 border-t border-slate-100 dark:border-slate-700 space-y-1">
        <button
          onClick={toggleTheme}
          className="flex items-center gap-2.5 px-3 py-1.5 w-full rounded-lg text-xs text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-700"
        >
          {theme === 'dark' ? <Sun className="h-3.5 w-3.5" /> : <Moon className="h-3.5 w-3.5" />}
          {theme === 'dark' ? 'Light Mode' : 'Dark Mode'}
        </button>
        <button
          onClick={logout}
          className="flex items-center gap-2.5 px-3 py-1.5 w-full rounded-lg text-xs text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20"
        >
          <LogOut className="h-3.5 w-3.5" />
          Sign Out
        </button>
        <div className="px-3 pt-1 text-[11px] text-slate-400 truncate">
          {user?.full_name} <span className="uppercase text-[10px] font-bold text-primary-600">({role})</span>
        </div>
      </div>
    </div>
  );
}
