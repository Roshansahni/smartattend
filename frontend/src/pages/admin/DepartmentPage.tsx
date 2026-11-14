import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { api } from '@/services/api';
import { Card, CardContent, CardHeader } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import toast from 'react-hot-toast';
import { Building2, Plus, Users, BookOpen } from 'lucide-react';

export default function DepartmentPage() {
  const [departments, setDepartments] = useState([
    { id: '1', code: 'CSE', name: 'Computer Science & Engineering', students: 120, faculty: 12, courses: 8 },
    { id: '2', code: 'ECE', name: 'Electronics & Communication Engineering', students: 95, faculty: 9, courses: 6 },
    { id: '3', code: 'IT', name: 'Information Technology', students: 110, faculty: 10, courses: 7 },
    { id: '4', code: 'ME', name: 'Mechanical Engineering', students: 80, faculty: 8, courses: 5 },
  ]);

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-slate-900 dark:text-white">Department Management</h2>
          <p className="text-sm text-slate-500">Academic departments, student allocations, and faculty rosters</p>
        </div>
        <Button leftIcon={<Plus className="h-4 w-4" />}>Add Department</Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {departments.map(d => (
          <Card key={d.id} className="hover:shadow-md transition">
            <CardHeader>
              <div className="flex items-center justify-between">
                <span className="font-bold font-mono text-xs bg-primary-50 text-primary-600 dark:bg-primary-950/40 px-2.5 py-1 rounded-md">
                  {d.code}
                </span>
                <Badge variant="success">Active Division</Badge>
              </div>
              <h3 className="font-bold text-lg mt-2 text-slate-900 dark:text-white">{d.name}</h3>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-3 gap-2 pt-2 border-t border-slate-100 dark:border-slate-800 text-center">
                <div className="p-2 bg-slate-50 dark:bg-slate-800 rounded-lg">
                  <span className="text-xs text-slate-400 block font-medium">Students</span>
                  <span className="text-base font-bold text-slate-900 dark:text-white">{d.students}</span>
                </div>
                <div className="p-2 bg-slate-50 dark:bg-slate-800 rounded-lg">
                  <span className="text-xs text-slate-400 block font-medium">Faculty</span>
                  <span className="text-base font-bold text-slate-900 dark:text-white">{d.faculty}</span>
                </div>
                <div className="p-2 bg-slate-50 dark:bg-slate-800 rounded-lg">
                  <span className="text-xs text-slate-400 block font-medium">Courses</span>
                  <span className="text-base font-bold text-slate-900 dark:text-white">{d.courses}</span>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
