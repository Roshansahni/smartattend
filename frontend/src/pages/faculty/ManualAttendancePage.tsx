import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { studentService } from '@/services/student.service';
import { courseService } from '@/services/course.service';
import { attendanceService } from '@/services/attendance.service';
import { Card, CardContent, CardHeader } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import toast from 'react-hot-toast';
import { UserCheck, ShieldAlert, Check, X, Search } from 'lucide-react';

export default function ManualAttendancePage() {
  const [search, setSearch] = useState('');
  const [auditReason, setAuditReason] = useState('Faculty Manual Verification');
  const [markedStudents, setMarkedStudents] = useState<Record<string, boolean>>({});

  const { data: studentsData } = useQuery({
    queryKey: ['students-manual'],
    queryFn: () => studentService.getStudents(1, 50),
  });

  const students = studentsData?.items || [];
  const filtered = students.filter(s =>
    s.user.full_name.toLowerCase().includes(search.toLowerCase()) ||
    s.enrollment_number.toLowerCase().includes(search.toLowerCase())
  );

  const toggleAttendance = (studentId: string, current: boolean) => {
    setMarkedStudents(prev => ({
      ...prev,
      [studentId]: !current
    }));
    toast.success(`Updated attendance record with audit reason: "${auditReason}"`);
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between sm:items-center gap-4">
        <div>
          <h2 className="text-2xl font-bold text-slate-900 dark:text-white">Manual Attendance & Corrections</h2>
          <p className="text-sm text-slate-500">Override attendance with mandatory security audit logging</p>
        </div>

        <div className="flex items-center gap-2">
          <label className="text-xs font-semibold text-slate-500 whitespace-nowrap">Audit Log Reason:</label>
          <input
            type="text"
            value={auditReason}
            onChange={(e) => setAuditReason(e.target.value)}
            className="px-3 py-1.5 text-xs bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg w-64"
          />
        </div>
      </div>

      <Card>
        <CardHeader className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="relative w-full sm:w-72">
            <Search className="h-4 w-4 absolute left-3 top-2.5 text-slate-400" />
            <input
              type="text"
              placeholder="Search by student name or roll no..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-9 pr-3 py-2 text-xs bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg"
            />
          </div>
          <span className="text-xs text-slate-400">Course: CS401 • Lecture 14</span>
        </CardHeader>
        <CardContent className="p-0">
          <table className="w-full text-sm">
            <thead className="bg-slate-50 dark:bg-slate-800/50 text-xs text-slate-400">
              <tr>
                <th className="text-left px-6 py-3 font-semibold">Student Name</th>
                <th className="text-left px-6 py-3 font-semibold">Enrollment No.</th>
                <th className="text-center px-6 py-3 font-semibold">Current Status</th>
                <th className="text-right px-6 py-3 font-semibold">Manual Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-700">
              {filtered.map(s => {
                const isPresent = markedStudents[s.id] ?? true;
                return (
                  <tr key={s.id} className="hover:bg-slate-50 dark:hover:bg-slate-800/40">
                    <td className="px-6 py-3 font-medium text-slate-900 dark:text-white">{s.user.full_name}</td>
                    <td className="px-6 py-3 font-mono text-xs text-slate-500">{s.enrollment_number}</td>
                    <td className="px-6 py-3 text-center">
                      <Badge variant={isPresent ? 'success' : 'danger'}>
                        {isPresent ? 'Present' : 'Absent'}
                      </Badge>
                    </td>
                    <td className="px-6 py-3 text-right">
                      <Button
                        size="sm"
                        variant={isPresent ? 'outline' : 'primary'}
                        onClick={() => toggleAttendance(s.id, isPresent)}
                        className="text-xs"
                      >
                        {isPresent ? 'Mark Absent' : 'Mark Present'}
                      </Button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </CardContent>
      </Card>
    </div>
  );
}
