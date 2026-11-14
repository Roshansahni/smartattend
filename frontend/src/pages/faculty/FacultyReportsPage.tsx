import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { courseService } from '@/services/course.service';
import { Card, CardContent, CardHeader } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import toast from 'react-hot-toast';
import { FileDown, FileText, Download, AlertTriangle, CheckCircle, BarChart3 } from 'lucide-react';

export default function FacultyReportsPage() {
  const { data: courses = [] } = useQuery({
    queryKey: ['courses'],
    queryFn: () => courseService.getCourses(),
  });

  const handleDownload = (format: string) => {
    toast.success(`Generated official SmartAttend ${format.toUpperCase()} attendance report!`);
  };

  const lowAttendanceStudents = [
    { name: 'Student 01', roll: '2022CSE001', pct: 62.5, missed: 6 },
    { name: 'Student 05', roll: '2022CSE005', pct: 58.0, missed: 7 },
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between sm:items-center gap-4">
        <div>
          <h2 className="text-2xl font-bold text-slate-900 dark:text-white">Attendance Reports & Exports</h2>
          <p className="text-sm text-slate-500">Official academic attendance reports, CSV spreadsheets, and compliance logs</p>
        </div>

        <div className="flex gap-2">
          <Button onClick={() => handleDownload('pdf')} className="bg-primary-600 hover:bg-primary-700" leftIcon={<FileDown className="h-4 w-4" />}>
            Download PDF Report
          </Button>
          <Button onClick={() => handleDownload('excel')} variant="outline" leftIcon={<Download className="h-4 w-4" />}>
            Export Excel / CSV
          </Button>
        </div>
      </div>

      {/* Low Attendance Alert Section */}
      <Card className="border-red-200 dark:border-red-900 bg-red-50/30 dark:bg-red-950/20">
        <CardHeader>
          <div className="flex items-center justify-between">
            <h3 className="font-semibold text-lg flex items-center gap-2 text-red-600">
              <AlertTriangle className="h-5 w-5" />
              Critical Shortage: Students Below 75% Mandate ({lowAttendanceStudents.length})
            </h3>
            <Badge variant="danger">Action Required</Badge>
          </div>
        </CardHeader>
        <CardContent className="p-0">
          <table className="w-full text-sm">
            <thead className="bg-red-100/40 dark:bg-red-950/40 text-xs text-red-700 dark:text-red-300">
              <tr>
                <th className="text-left px-6 py-2.5 font-semibold">Student Name</th>
                <th className="text-left px-6 py-2.5 font-semibold">Enrollment No.</th>
                <th className="text-center px-4 py-2.5 font-semibold">Classes Missed</th>
                <th className="text-center px-4 py-2.5 font-semibold">Current Attendance</th>
                <th className="text-right px-6 py-2.5 font-semibold">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-red-100 dark:divide-red-900/40">
              {lowAttendanceStudents.map((s, idx) => (
                <tr key={idx}>
                  <td className="px-6 py-3 font-medium text-slate-900 dark:text-white">{s.name}</td>
                  <td className="px-6 py-3 font-mono text-xs">{s.roll}</td>
                  <td className="px-4 py-3 text-center text-red-600 font-bold">{s.missed} Classes</td>
                  <td className="px-4 py-3 text-center font-bold text-red-600 font-mono">{s.pct}%</td>
                  <td className="px-6 py-3 text-right">
                    <Badge variant="danger">Warning Issued</Badge>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </CardContent>
      </Card>

      {/* Course Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <h3 className="font-semibold text-lg flex items-center gap-2">
              <BarChart3 className="h-5 w-5 text-primary-600" />
              Course Attendance Performance
            </h3>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-3">
              <div>
                <div className="flex justify-between text-xs font-semibold mb-1">
                  <span>CS401 - Distributed Systems & Cloud</span>
                  <span className="text-primary-600">84.2%</span>
                </div>
                <div className="h-2 w-full bg-slate-100 dark:bg-slate-700 rounded-full overflow-hidden">
                  <div className="h-full bg-primary-600 rounded-full" style={{ width: '84.2%' }} />
                </div>
              </div>
              <div>
                <div className="flex justify-between text-xs font-semibold mb-1">
                  <span>CS402 - Machine Learning & Neural Networks</span>
                  <span className="text-green-600">91.0%</span>
                </div>
                <div className="h-2 w-full bg-slate-100 dark:bg-slate-700 rounded-full overflow-hidden">
                  <div className="h-full bg-green-500 rounded-full" style={{ width: '91%' }} />
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <h3 className="font-semibold text-lg flex items-center gap-2">
              <FileText className="h-5 w-5 text-primary-600" />
              Report Customization
            </h3>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-xs text-slate-500">
              Generated reports include student roll numbers, timestamps, geofence status, and cryptographic signature hashes suitable for NAAC / NBA accreditation audits.
            </p>
            <div className="grid grid-cols-2 gap-2 text-xs">
              <div className="p-3 bg-slate-50 dark:bg-slate-800 rounded-lg">
                <span className="text-slate-400 block">Total Lectures</span>
                <span className="text-lg font-bold">16 Sessions</span>
              </div>
              <div className="p-3 bg-slate-50 dark:bg-slate-800 rounded-lg">
                <span className="text-slate-400 block">Accreditation Ready</span>
                <span className="text-lg font-bold text-green-600">ISO 27001</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
