import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { courseService } from '@/services/course.service';
import { Card, CardContent, CardHeader } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Link } from 'react-router-dom';
import { BookOpen, Plus } from 'lucide-react';

export default function FacultyDashboard() {
  const { data: courses = [] } = useQuery({
    queryKey: ['courses'],
    queryFn: () => courseService.getCourses(),
  });

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold">Faculty Portal</h2>
          <p className="text-sm text-slate-500">Manage courses and conduct live QR attendance sessions</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {courses.map(c => (
          <Card key={c.id}>
            <CardHeader>
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-primary-600 bg-primary-50 px-2 py-0.5 rounded">{c.code}</span>
                <span className="text-xs text-slate-400">Sem {c.semester}</span>
              </div>
              <h3 className="font-semibold text-lg mt-2">{c.name}</h3>
            </CardHeader>
            <CardContent>
              <p className="text-xs text-slate-500 mb-4">{c.description || 'Active academic course'}</p>
              <Link to={`/faculty/session/${c.id}`}>
                <Button size="sm" className="w-full">Open Session Room</Button>
              </Link>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
