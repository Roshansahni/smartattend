import React from 'react';
import { NavLink } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { useTheme } from '@/context/ThemeContext';
import {
  LayoutDashboard, QrCode, ClipboardList, Users, GraduationCap,
  CalendarCheck, Sun, Moon, LogOut
} from 'lucide-react';
import { cn } from '@/utils/cn';

export default function Sidebar() {
  const { role, user, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();

  const studentNav = [
    { to: '/student/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
    { to: '/student/scan', icon: QrCode, label: 'Scan QR' },
    { to: '/student/attendance', icon: ClipboardList, label: 'My Attendance' },
  ];

  const facultyNav = [
    { to: '/faculty/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  ];

  const adminNav = [
    { to: '/admin/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
    { to: '/admin/students', icon: GraduationCap, label: 'Students' },
    { to: '/admin/faculty', icon: Users, label: 'Faculty' },
  ];

  const navItems = role === 'student' ? studentNav : role === 'faculty' ? facultyNav : adminNav;

  return (
    <div className="w-64 bg-white dark:bg-slate-800 border-r border-slate-200 dark:border-slate-700 flex flex-col h-full">
      <div className="p-6 border-b border-slate-100 dark:border-slate-700 flex items-center gap-2">
        <div className="h-8 w-8 bg-primary-600 rounded-lg flex items-center justify-center text-white">
          <CalendarCheck className="h-5 w-5" />
        </div>
        <span className="font-bold text-slate-900 dark:text-white text-lg">SmartAttend</span>
      </div>

      <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
        {navItems.map(item => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) => cn(
              'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all',
              isActive
                ? 'bg-primary-600 text-white'
                : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-700'
            )}
          >
            <item.icon className="h-4 w-4" />
            {item.label}
          </NavLink>
        ))}
      </nav>

      <div className="p-4 border-t border-slate-100 dark:border-slate-700 space-y-2">
        <button onClick={toggleTheme} className="flex items-center gap-3 px-3 py-2 w-full rounded-lg text-sm text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-700">
          {theme === 'dark' ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
          {theme === 'dark' ? 'Light' : 'Dark'} Mode
        </button>
        <button onClick={logout} className="flex items-center gap-3 px-3 py-2 w-full rounded-lg text-sm text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20">
          <LogOut className="h-4 w-4" />
          Sign Out
        </button>
        <div className="px-3 text-xs text-slate-400 truncate">{user?.full_name} ({role})</div>
      </div>
    </div>
  );
}
