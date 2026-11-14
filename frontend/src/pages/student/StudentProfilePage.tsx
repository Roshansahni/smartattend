import React from 'react';
import { useAuth } from '@/context/AuthContext';
import { Card, CardContent, CardHeader } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { User, Mail, Shield, GraduationCap, Building, Key } from 'lucide-react';
import { Button } from '@/components/ui/Button';

export default function StudentProfilePage() {
  const { user, role } = useAuth();

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-900 dark:text-white">Student Profile</h2>
        <p className="text-sm text-slate-500">Institutional records and ERP credential details</p>
      </div>

      <Card>
        <CardHeader>
          <div className="flex items-center gap-4">
            <div className="h-16 w-16 bg-primary-600 rounded-2xl flex items-center justify-center text-white text-2xl font-bold">
              {user?.full_name?.charAt(0) || 'S'}
            </div>
            <div>
              <h3 className="text-xl font-bold text-slate-900 dark:text-white">{user?.full_name}</h3>
              <p className="text-xs text-slate-400 font-mono">{user?.email}</p>
              <div className="mt-2 flex gap-2">
                <Badge variant="success">Active Enrolled</Badge>
                <Badge variant="info">Semester 7</Badge>
              </div>
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-4 pt-4 border-t">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
            <div className="p-3 bg-slate-50 dark:bg-slate-800 rounded-xl">
              <span className="text-xs text-slate-400 block font-medium">Roll / Enrollment No.</span>
              <span className="font-mono font-bold text-slate-800 dark:text-slate-100">2022CSE001</span>
            </div>
            <div className="p-3 bg-slate-50 dark:bg-slate-800 rounded-xl">
              <span className="text-xs text-slate-400 block font-medium">Department</span>
              <span className="font-bold text-slate-800 dark:text-slate-100">Computer Science & Engineering</span>
            </div>
            <div className="p-3 bg-slate-50 dark:bg-slate-800 rounded-xl">
              <span className="text-xs text-slate-400 block font-medium">Academic Batch</span>
              <span className="font-bold text-slate-800 dark:text-slate-100">B.Tech (2022 – 2026)</span>
            </div>
            <div className="p-3 bg-slate-50 dark:bg-slate-800 rounded-xl">
              <span className="text-xs text-slate-400 block font-medium">Attendance Mandate</span>
              <span className="font-bold text-green-600">75% Minimum Required</span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
