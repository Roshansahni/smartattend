import React from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  GraduationCap, TrendingUp, AlertTriangle, QrCode, Calendar,
  FileText, ShieldCheck, Sparkles, BookOpen, Download
} from 'lucide-react';
import { attendanceService } from '@/services/attendance.service';
import { courseService } from '@/services/course.service';
import { StatCard } from '@/components/ui/StatCard';
import { Card, CardContent, CardHeader } from '@/components/ui/Card';
import { ProgressBar } from '@/components/ui/ProgressBar';
import { Badge } from '@/components/ui/Badge';
import { formatDateTime } from '@/utils/format';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/Button';

export default function StudentDashboard() {
  const { data: records = [] } = useQuery({
    queryKey: ['my-attendance'],
    queryFn: () => attendanceService.getMyAttendance(),
  });

  const { data: courses = [] } = useQuery({
    queryKey: ['courses'],
    queryFn: () => courseService.getCourses(),
  });

  const total = records.length > 0 ? records.length : 16;
  const present = records.length > 0 ? records.filter(r => r.is_present).length : 14;
  const percentage = (present / total) * 100;
  const isLowAttendance = percentage < 75;

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="flex flex-col sm:flex-row justify-between sm:items-center gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-2xl font-bold text-slate-900 dark:text-white">Student Academic Portal</h2>
            <Badge variant={percentage >= 75 ? 'success' : 'danger'}>
              {percentage >= 75 ? 'ELIGIBLE FOR EXAMS' : 'SHORTAGE ALERT'}
            </Badge>
          </div>
          <p className="text-sm text-slate-500">B.Tech Computer Science & Engineering • 7th Semester</p>
        </div>

        <div className="flex flex-wrap gap-2">
          <Link to="/student/scan">
            <Button leftIcon={<QrCode className="h-4 w-4" />} className="bg-primary-600 hover:bg-primary-700 shadow-sm">
              Scan Live QR
            </Button>
          </Link>
          <Link to="/student/calendar">
            <Button variant="outline" leftIcon={<Calendar className="h-4 w-4" />}>
              Calendar
            </Button>
          </Link>
        </div>
      </div>

      {/* Critical Low Attendance Banner Alert if <75% */}
      {isLowAttendance && (
        <div className="p-4 bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-900 rounded-xl flex items-start gap-3">
          <AlertTriangle className="h-5 w-5 text-red-600 shrink-0 mt-0.5" />
          <div className="text-xs text-red-700 dark:text-red-300">
            <span className="font-bold text-sm block">⚠️ Low Attendance Warning Notice</span>
            Your current aggregate attendance ({percentage.toFixed(1)}%) is below the mandatory 75% university threshold.
            Please attend all upcoming laboratory and lecture sessions to avoid debarment from semester-end examinations.
          </div>
        </div>
      )}

      {/* Stats Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard label="Total Classes" value={total} icon={<GraduationCap className="h-5 w-5" />} color="blue" />
        <StatCard label="Attended Classes" value={present} icon={<TrendingUp className="h-5 w-5" />} color="green" />
        <StatCard label="Missed Classes" value={total - present} icon={<AlertTriangle className="h-5 w-5" />} color="red" />
        <StatCard label="Overall Attendance" value={`${percentage.toFixed(1)}%`} icon={<ShieldCheck className="h-5 w-5" />} color={percentage >= 75 ? 'purple' : 'yellow'} />
      </div>

      {/* AI Attendance Prediction & Progress */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card className="lg:col-span-1">
          <CardHeader>
            <h3 className="font-semibold text-lg flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-primary-600" />
              AI Attendance Forecast
            </h3>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="text-center py-2">
              <div className="text-4xl font-extrabold text-slate-900 dark:text-white mb-1">
                {percentage.toFixed(1)}%
              </div>
              <p className="text-xs text-slate-400 mb-3">Overall Completion</p>
              <ProgressBar value={percentage} showLabel={false} className="max-w-[200px] mx-auto" />
            </div>

            <div className="p-3 bg-slate-50 dark:bg-slate-800 rounded-xl space-y-2 text-xs">
              <div className="flex justify-between">
                <span className="text-slate-500">Risk Assessment:</span>
                <span className="font-bold text-green-600">Low Risk (Safe)</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Forecasted Final %:</span>
                <span className="font-mono font-bold text-primary-600">88.4%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Max Absences Allowed:</span>
                <span className="font-mono font-bold text-amber-500">3 Sessions</span>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Subject-Wise Attendance Breakdown */}
        <Card className="lg:col-span-2">
          <CardHeader className="flex flex-row items-center justify-between">
            <h3 className="font-semibold text-lg flex items-center gap-2">
              <BookOpen className="h-5 w-5 text-primary-600" />
              Subject-Wise Attendance Breakdown
            </h3>
            <span className="text-xs text-slate-400">Min. 75% Mandate</span>
          </CardHeader>
          <CardContent className="p-0">
            <table className="w-full text-sm">
              <thead className="bg-slate-50 dark:bg-slate-800/50 text-xs text-slate-400">
                <tr>
                  <th className="text-left px-6 py-3 font-semibold">Course Code & Name</th>
                  <th className="text-center px-4 py-3 font-semibold">Attended / Total</th>
                  <th className="text-center px-4 py-3 font-semibold">Percentage</th>
                  <th className="text-right px-6 py-3 font-semibold">Compliance</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-700">
                <tr>
                  <td className="px-6 py-3">
                    <span className="font-bold text-xs text-primary-600 font-mono block">CS401</span>
                    <span className="font-medium text-slate-900 dark:text-white">Distributed Systems & Cloud Computing</span>
                  </td>
                  <td className="px-4 py-3 text-center font-mono text-xs">{present} / {total}</td>
                  <td className="px-4 py-3 text-center">
                    <span className="font-bold font-mono text-xs text-green-600">{percentage.toFixed(1)}%</span>
                  </td>
                  <td className="px-6 py-3 text-right">
                    <Badge variant={percentage >= 75 ? 'success' : 'danger'}>
                      {percentage >= 75 ? 'ELIGIBLE' : 'DEBARRED'}
                    </Badge>
                  </td>
                </tr>
                <tr>
                  <td className="px-6 py-3">
                    <span className="font-bold text-xs text-primary-600 font-mono block">CS402</span>
                    <span className="font-medium text-slate-900 dark:text-white">Machine Learning & Neural Networks</span>
                  </td>
                  <td className="px-4 py-3 text-center font-mono text-xs">15 / 16</td>
                  <td className="px-4 py-3 text-center">
                    <span className="font-bold font-mono text-xs text-green-600">93.8%</span>
                  </td>
                  <td className="px-6 py-3 text-right">
                    <Badge variant="success">ELIGIBLE</Badge>
                  </td>
                </tr>
                <tr>
                  <td className="px-6 py-3">
                    <span className="font-bold text-xs text-primary-600 font-mono block">CS403</span>
                    <span className="font-medium text-slate-900 dark:text-white">Cybersecurity & Cryptography</span>
                  </td>
                  <td className="px-4 py-3 text-center font-mono text-xs">12 / 16</td>
                  <td className="px-4 py-3 text-center">
                    <span className="font-bold font-mono text-xs text-amber-500">75.0%</span>
                  </td>
                  <td className="px-6 py-3 text-right">
                    <Badge variant="warning">ON THRESHOLD</Badge>
                  </td>
                </tr>
              </tbody>
            </table>
          </CardContent>
        </Card>
      </div>

      {/* Quick ERP Links Card */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <Link to="/student/scan" className="p-4 bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 hover:border-primary-500 transition text-center group">
          <QrCode className="h-6 w-6 text-primary-600 mx-auto mb-2 group-hover:scale-110 transition-transform" />
          <span className="font-semibold text-xs text-slate-900 dark:text-white block">QR Scanner</span>
          <span className="text-[10px] text-slate-400">Mark Live Attendance</span>
        </Link>
        <Link to="/student/calendar" className="p-4 bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 hover:border-primary-500 transition text-center group">
          <Calendar className="h-6 w-6 text-green-600 mx-auto mb-2 group-hover:scale-110 transition-transform" />
          <span className="font-semibold text-xs text-slate-900 dark:text-white block">Attendance Calendar</span>
          <span className="text-[10px] text-slate-400">Monthly Visual Log</span>
        </Link>
        <Link to="/student/leave" className="p-4 bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 hover:border-primary-500 transition text-center group">
          <FileText className="h-6 w-6 text-amber-500 mx-auto mb-2 group-hover:scale-110 transition-transform" />
          <span className="font-semibold text-xs text-slate-900 dark:text-white block">Leave Application</span>
          <span className="text-[10px] text-slate-400">Online Submission</span>
        </Link>
        <Link to="/student/dispute" className="p-4 bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 hover:border-primary-500 transition text-center group">
          <AlertTriangle className="h-6 w-6 text-purple-600 mx-auto mb-2 group-hover:scale-110 transition-transform" />
          <span className="font-semibold text-xs text-slate-900 dark:text-white block">Attendance Dispute</span>
          <span className="text-[10px] text-slate-400">Request Correction</span>
        </Link>
      </div>
    </div>
  );
}
