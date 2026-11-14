import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { GraduationCap, TrendingUp, AlertTriangle } from 'lucide-react';
import { attendanceService } from '@/services/attendance.service';
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

  const total = records.length;
  const present = records.filter(r => r.is_present).length;
  const percentage = total > 0 ? (present / total) * 100 : 0;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold">Student Dashboard</h2>
          <p className="text-sm text-slate-500">Welcome to your attendance overview</p>
        </div>
        <Link to="/student/scan">
          <Button>Scan QR Code</Button>
        </Link>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <StatCard label="Total Classes" value={total} icon={<GraduationCap className="h-5 w-5" />} color="blue" />
        <StatCard label="Present" value={present} icon={<TrendingUp className="h-5 w-5" />} color="green" />
        <StatCard label="Absent" value={total - present} icon={<AlertTriangle className="h-5 w-5" />} color="red" />
      </div>

      <Card>
        <CardHeader><h3 className="font-semibold">Overall Attendance</h3></CardHeader>
        <CardContent>
          <div className="text-center py-4">
            <div className="text-5xl font-bold mb-2">{percentage.toFixed(1)}%</div>
            <ProgressBar value={percentage} showLabel={false} className="max-w-xs mx-auto" />
            {percentage < 75 && total > 0 && (
              <p className="text-xs text-red-500 mt-2 font-medium">⚠️ Warning: Attendance is below 75% requirement.</p>
            )}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader><h3 className="font-semibold">Recent Attendance Records</h3></CardHeader>
        <CardContent>
          {records.length > 0 ? (
            <div className="divide-y divide-slate-100 dark:divide-slate-700">
              {records.slice(0, 5).map(r => (
                <div key={r.id} className="py-2.5 flex justify-between items-center text-sm">
                  <span>{formatDateTime(r.marked_at)}</span>
                  <Badge variant={r.is_present ? 'success' : 'danger'}>{r.is_present ? 'Present' : 'Absent'}</Badge>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-slate-400 text-center py-6">No records yet.</p>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
