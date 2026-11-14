import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { attendanceService } from '@/services/attendance.service';
import { Card, CardContent, CardHeader } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Calendar as CalendarIcon, ChevronLeft, ChevronRight, CheckCircle2, XCircle, AlertCircle } from 'lucide-react';
import { Button } from '@/components/ui/Button';

export default function AttendanceCalendarPage() {
  const [currentMonth, setCurrentMonth] = useState('November 2026');

  // Days in November (1 to 30)
  const daysInMonth = Array.from({ length: 30 }, (_, i) => i + 1);

  // Generate realistic ERP attendance records for November
  const attendanceMap: Record<number, 'present' | 'absent' | 'leave' | 'weekend'> = {};
  daysInMonth.forEach(day => {
    const dayOfWeek = (day + 5) % 7; // Nov 1 2026 starts on Sunday (day 0)
    if (dayOfWeek === 0 || dayOfWeek === 6) {
      attendanceMap[day] = 'weekend';
    } else if (day === 4 || day === 11) {
      attendanceMap[day] = 'absent';
    } else if (day === 9) {
      attendanceMap[day] = 'leave';
    } else if (day <= 14) {
      attendanceMap[day] = 'present';
    }
  });

  const presentCount = Object.values(attendanceMap).filter(v => v === 'present').length;
  const absentCount = Object.values(attendanceMap).filter(v => v === 'absent').length;
  const leaveCount = Object.values(attendanceMap).filter(v => v === 'leave').length;
  const totalWorking = presentCount + absentCount + leaveCount;
  const monthlyPct = totalWorking > 0 ? ((presentCount / totalWorking) * 100).toFixed(1) : '0';

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between sm:items-center gap-4">
        <div>
          <h2 className="text-2xl font-bold text-slate-900 dark:text-white">Attendance Calendar</h2>
          <p className="text-sm text-slate-500">Visual monthly attendance log and compliance tracking</p>
        </div>

        <div className="flex items-center gap-2 bg-white dark:bg-slate-800 p-1.5 rounded-xl border border-slate-200 dark:border-slate-700">
          <Button variant="outline" size="sm" className="h-8 w-8 p-0"><ChevronLeft className="h-4 w-4" /></Button>
          <span className="font-semibold text-sm px-3">{currentMonth}</span>
          <Button variant="outline" size="sm" className="h-8 w-8 p-0"><ChevronRight className="h-4 w-4" /></Button>
        </div>
      </div>

      {/* Monthly Summary Badges */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="p-4 bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 text-center">
          <p className="text-xs text-slate-400 font-medium">Monthly Percentage</p>
          <p className="text-2xl font-bold text-primary-600 mt-1">{monthlyPct}%</p>
        </div>
        <div className="p-4 bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 text-center">
          <p className="text-xs text-slate-400 font-medium">Days Present</p>
          <p className="text-2xl font-bold text-green-600 mt-1">{presentCount}</p>
        </div>
        <div className="p-4 bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 text-center">
          <p className="text-xs text-slate-400 font-medium">Days Absent</p>
          <p className="text-2xl font-bold text-red-500 mt-1">{absentCount}</p>
        </div>
        <div className="p-4 bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 text-center">
          <p className="text-xs text-slate-400 font-medium">Approved Leave</p>
          <p className="text-2xl font-bold text-amber-500 mt-1">{leaveCount}</p>
        </div>
      </div>

      {/* Interactive Calendar Grid */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <h3 className="font-semibold text-lg flex items-center gap-2">
              <CalendarIcon className="h-5 w-5 text-primary-600" />
              November 2026 Academic Days
            </h3>
            <div className="flex items-center gap-4 text-xs font-medium">
              <span className="flex items-center gap-1.5"><span className="h-2.5 w-2.5 rounded-full bg-green-500" /> Present</span>
              <span className="flex items-center gap-1.5"><span className="h-2.5 w-2.5 rounded-full bg-red-500" /> Absent</span>
              <span className="flex items-center gap-1.5"><span className="h-2.5 w-2.5 rounded-full bg-amber-400" /> Leave</span>
              <span className="flex items-center gap-1.5"><span className="h-2.5 w-2.5 rounded-full bg-slate-300 dark:bg-slate-600" /> Weekend</span>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-7 gap-2 text-center text-xs font-semibold text-slate-400 mb-2">
            <span>SUN</span><span>MON</span><span>TUE</span><span>WED</span><span>THU</span><span>FRI</span><span>SAT</span>
          </div>

          <div className="grid grid-cols-7 gap-2">
            {daysInMonth.map(day => {
              const status = attendanceMap[day];
              return (
                <div
                  key={day}
                  className={`p-3 rounded-xl border text-center transition-all ${
                    status === 'present'
                      ? 'bg-green-50 dark:bg-green-950/40 border-green-200 dark:border-green-800 text-green-700 dark:text-green-300'
                      : status === 'absent'
                      ? 'bg-red-50 dark:bg-red-950/40 border-red-200 dark:border-red-800 text-red-600 dark:text-red-300'
                      : status === 'leave'
                      ? 'bg-amber-50 dark:bg-amber-950/40 border-amber-200 dark:border-amber-800 text-amber-600 dark:text-amber-300'
                      : 'bg-slate-50 dark:bg-slate-800/40 border-slate-100 dark:border-slate-800 text-slate-400'
                  }`}
                >
                  <div className="font-bold text-sm">{day}</div>
                  <div className="text-[10px] mt-1 font-medium capitalize">
                    {status === 'present' ? '✓ Present' : status === 'absent' ? '✗ Absent' : status === 'leave' ? '○ Leave' : 'Off'}
                  </div>
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
