import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { attendanceService } from '@/services/attendance.service';
import { Card, CardContent, CardHeader } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { formatDateTime } from '@/utils/format';

export default function AttendanceHistoryPage() {
  const { data: records = [], isLoading } = useQuery({
    queryKey: ['my-attendance'],
    queryFn: () => attendanceService.getMyAttendance(),
  });

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Attendance History</h2>
      <Card>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-slate-50 dark:bg-slate-700/50">
                <tr>
                  <th className="text-left px-6 py-3 font-medium text-slate-500">Date & Time</th>
                  <th className="text-left px-6 py-3 font-medium text-slate-500">Method</th>
                  <th className="text-left px-6 py-3 font-medium text-slate-500">Status</th>
                  <th className="text-left px-6 py-3 font-medium text-slate-500">Audit</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-700">
                {records.map(r => (
                  <tr key={r.id}>
                    <td className="px-6 py-3">{formatDateTime(r.marked_at)}</td>
                    <td className="px-6 py-3">{r.verification_method.toUpperCase()}</td>
                    <td className="px-6 py-3"><Badge variant={r.is_present ? 'success' : 'danger'}>{r.is_present ? 'Present' : 'Absent'}</Badge></td>
                    <td className="px-6 py-3">{r.is_edited ? <Badge variant="warning">Manual Edit</Badge> : '—'}</td>
                  </tr>
                ))}
                {records.length === 0 && !isLoading && (
                  <tr><td colSpan={4} className="text-center py-8 text-slate-400">No attendance records found.</td></tr>
                )}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
