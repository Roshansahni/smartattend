import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { erpService } from '@/services/erp.service';
import { Card, CardContent, CardHeader } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Calendar, Plus, Clock, MapPin, User, BookOpen } from 'lucide-react';
import toast from 'react-hot-toast';

export default function TimetableManagementPage() {
  const { data: schedule = [] } = useQuery({
    queryKey: ['admin-timetable'],
    queryFn: () => erpService.getTimetable(),
  });

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-slate-900 dark:text-white">Timetable & Schedule Management</h2>
          <p className="text-sm text-slate-500">Configure lecture slots, faculty room assignments, and academic time slots</p>
        </div>
        <Button leftIcon={<Plus className="h-4 w-4" />} onClick={() => toast.success('Slot schedule modal opened')}>
          Create Lecture Slot
        </Button>
      </div>

      <Card>
        <CardHeader>
          <h3 className="font-semibold text-lg flex items-center gap-2">
            <Calendar className="h-5 w-5 text-primary-600" />
            Master Institutional Schedule ({schedule.length} active slots)
          </h3>
        </CardHeader>
        <CardContent className="p-0">
          <table className="w-full text-sm">
            <thead className="bg-slate-50 dark:bg-slate-800/50 text-xs text-slate-400">
              <tr>
                <th className="text-left px-6 py-3 font-semibold">Day & Time</th>
                <th className="text-left px-6 py-3 font-semibold">Course</th>
                <th className="text-left px-6 py-3 font-semibold">Assigned Faculty</th>
                <th className="text-center px-4 py-3 font-semibold">Room / Lab</th>
                <th className="text-center px-4 py-3 font-semibold">Semester & Sec</th>
                <th className="text-right px-6 py-3 font-semibold">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-700">
              {schedule.map((item: any) => (
                <tr key={item.id} className="hover:bg-slate-50 dark:hover:bg-slate-800/30">
                  <td className="px-6 py-3 font-medium text-slate-900 dark:text-white">
                    <span className="font-bold text-primary-600 block">{item.day}</span>
                    <span className="text-xs text-slate-400 font-mono">{item.start_time} – {item.end_time}</span>
                  </td>
                  <td className="px-6 py-3">
                    <span className="font-bold font-mono text-xs text-slate-500">{item.course_code}</span>
                    <span className="block text-slate-900 dark:text-white">{item.course_name}</span>
                  </td>
                  <td className="px-6 py-3 text-slate-600 dark:text-slate-300">{item.faculty_name}</td>
                  <td className="px-4 py-3 text-center">
                    <Badge variant="info">{item.room_number}</Badge>
                  </td>
                  <td className="px-4 py-3 text-center font-mono text-xs">
                    Sem {item.semester} ({item.section})
                  </td>
                  <td className="px-6 py-3 text-right">
                    <Badge variant="success">Active</Badge>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </CardContent>
      </Card>
    </div>
  );
}
