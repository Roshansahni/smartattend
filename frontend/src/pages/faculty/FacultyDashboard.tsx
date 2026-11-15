import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { courseService } from '@/services/course.service';
import { Card, CardContent, CardHeader } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Link } from 'react-router-dom';
import { BookOpen, Users, Clock, Loader2, Sparkles } from 'lucide-react';

export default function FacultyDashboard() {
  const { data: courses = [], isLoading } = useQuery({
    queryKey: ['courses'],
    queryFn: () => courseService.getCourses(),
  });

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 bg-gradient-to-r from-primary-600 to-indigo-700 p-6 rounded-2xl text-white shadow-lg">
        <div>
          <h2 className="text-2xl font-bold">Faculty Portal & QR Command</h2>
          <p className="text-xs text-primary-100 mt-1">Start dynamic rotating QR attendance sessions and monitor classroom rosters in real time</p>
        </div>
        <Link to={`/faculty/session/${courses[0]?.id || 'bc8844a8-25a0-42e8-ad27-153ed7a89676'}`}>
          <Button size="lg" className="bg-white text-primary-700 hover:bg-primary-50 font-semibold shadow-md flex items-center gap-2 border-0">
            <Sparkles className="h-5 w-5 text-primary-600 animate-pulse" /> Launch Dynamic QR Session
          </Button>
        </Link>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center p-12 text-slate-400">
          <Loader2 className="h-6 w-6 animate-spin mr-2" />
          <span>Loading assigned courses...</span>
        </div>
      ) : courses.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {courses.map(c => (
            <Card key={c.id} className="hover:shadow-lg transition-shadow border-slate-200 dark:border-slate-700">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-primary-600 bg-primary-50 dark:bg-primary-900/40 px-2.5 py-1 rounded-md">{c.code}</span>
                  <span className="text-xs font-medium text-slate-400">Semester {c.semester}</span>
                </div>
                <h3 className="font-semibold text-lg mt-2 text-slate-900 dark:text-white">{c.name}</h3>
              </CardHeader>
              <CardContent>
                <p className="text-xs text-slate-500 dark:text-slate-400 mb-5 min-h-[32px]">{c.description || 'Active core CSE curriculum course'}</p>
                <div className="flex items-center gap-4 text-xs text-slate-400 mb-4 pb-4 border-b border-slate-100 dark:border-slate-800">
                  <div className="flex items-center gap-1"><Users className="h-3.5 w-3.5" /> 10 Enrolled</div>
                  <div className="flex items-center gap-1"><Clock className="h-3.5 w-3.5" /> {c.credit_hours} Credits</div>
                </div>
                <Link to={`/faculty/session/${c.id}`} className="block">
                  <Button size="sm" className="w-full flex items-center justify-center gap-2">
                    <Sparkles className="h-4 w-4" /> Start QR Attendance Session
                  </Button>
                </Link>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <Card className="p-8 text-center">
          <BookOpen className="h-10 w-10 text-slate-300 mx-auto mb-3" />
          <h3 className="font-semibold text-slate-700 dark:text-slate-200">No Courses Found</h3>
          <p className="text-xs text-slate-400 mt-1">Please ensure courses are assigned in the academic semester.</p>
        </Card>
      )}
    </div>
  );
}
