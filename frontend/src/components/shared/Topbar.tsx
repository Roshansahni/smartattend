import React from 'react';
import { useAuth } from '@/context/AuthContext';
import { Bell } from 'lucide-react';

export default function Topbar() {
  const { user } = useAuth();
  return (
    <header className="h-16 bg-white dark:bg-slate-800 border-b border-slate-200 dark:border-slate-700 flex items-center justify-between px-6">
      <div className="text-base font-semibold text-slate-900 dark:text-white">Smart Attendance System</div>
      <div className="flex items-center gap-4">
        <button className="p-2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200">
          <Bell className="h-5 w-5" />
        </button>
        <div className="h-8 w-8 bg-primary-600 rounded-full flex items-center justify-center text-white text-sm font-semibold">
          {user?.full_name?.charAt(0) || 'U'}
        </div>
      </div>
    </header>
  );
}
