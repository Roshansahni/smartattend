import React from 'react';
import { cn } from '@/utils/cn';
import { getAttendanceBg } from '@/utils/format';

export function ProgressBar({ value, showLabel = true, className }: { value: number; showLabel?: boolean; className?: string }) {
  return (
    <div className={cn('space-y-1', className)}>
      {showLabel && (
        <div className="flex justify-between text-xs font-medium">
          <span className="text-slate-600 dark:text-slate-400">Attendance</span>
          <span>{value.toFixed(1)}%</span>
        </div>
      )}
      <div className="h-2 bg-slate-100 dark:bg-slate-700 rounded-full overflow-hidden">
        <div
          className={cn('h-full rounded-full transition-all duration-500', getAttendanceBg(value))}
          style={{ width: `${Math.min(value, 100)}%` }}
        />
      </div>
    </div>
  );
}
