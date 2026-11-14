import React from 'react';
import { cn } from '@/utils/cn';

interface StatCardProps {
  label: string;
  value: string | number;
  icon: React.ReactNode;
  change?: string;
  color?: 'blue' | 'green' | 'yellow' | 'red' | 'purple';
}

const colors = {
  blue: 'bg-blue-500',
  green: 'bg-green-500',
  yellow: 'bg-yellow-500',
  red: 'bg-red-500',
  purple: 'bg-purple-500',
};

export function StatCard({ label, value, icon, change, color = 'blue' }: StatCardProps) {
  return (
    <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-6 shadow-sm">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-slate-500 dark:text-slate-400">{label}</p>
          <p className="text-3xl font-bold text-slate-900 dark:text-white mt-1">{value}</p>
          {change && <p className="text-xs text-slate-500 mt-1">{change}</p>}
        </div>
        <div className={cn('p-3 rounded-xl text-white', colors[color])}>
          {icon}
        </div>
      </div>
    </div>
  );
}
