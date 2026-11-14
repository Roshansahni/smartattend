import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { studentService } from '@/services/student.service';
import { Card, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';

export default function StudentsPage() {
  const { data } = useQuery({
    queryKey: ['students-list'],
    queryFn: () => studentService.getStudents(),
  });

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Student Directory</h2>
      <Card>
        <CardContent className="p-0">
          <table className="w-full text-sm">
            <thead className="bg-slate-50 dark:bg-slate-700/50">
              <tr>
                <th className="text-left px-6 py-3 font-medium text-slate-500">Name</th>
                <th className="text-left px-6 py-3 font-medium text-slate-500">Enrollment No.</th>
                <th className="text-left px-6 py-3 font-medium text-slate-500">Dept</th>
                <th className="text-left px-6 py-3 font-medium text-slate-500">Semester</th>
                <th className="text-left px-6 py-3 font-medium text-slate-500">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-700">
              {data?.items?.map(s => (
                <tr key={s.id}>
                  <td className="px-6 py-3 font-medium">{s.user.full_name}</td>
                  <td className="px-6 py-3 font-mono">{s.enrollment_number}</td>
                  <td className="px-6 py-3">{s.department.code}</td>
                  <td className="px-6 py-3">{s.semester}</td>
                  <td className="px-6 py-3"><Badge variant={s.is_active ? 'success' : 'danger'}>{s.is_active ? 'Active' : 'Inactive'}</Badge></td>
                </tr>
              ))}
            </tbody>
          </table>
        </CardContent>
      </Card>
    </div>
  );
}
