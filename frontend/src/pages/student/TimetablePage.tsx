import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { erpService } from '@/services/erp.service';
import { Card, CardContent, CardHeader } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Clock, BookOpen, MapPin, User, Calendar } from 'lucide-react';

export default function TimetablePage() {
  const [selectedDay, setSelectedDay] = useState('All');

  const { data: schedule = [], isLoading } = useQuery({
    queryKey: ['timetable'],
    queryFn: () => erpService.getTimetable(),
  });

  const days = ['All', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'];
  const filtered = selectedDay === 'All' ? schedule : schedule.filter((s: any) => s.day === selectedDay);

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between sm:items-center gap-4">
        <div>
          <h2 className="text-2xl font-bold text-slate-900 dark:text-white">Class Timetable</h2>
          <p className="text-sm text-slate-500">Semester 7 • Computer Science & Engineering • Section A</p>
        </div>

        {/* Day Filter Pills */}
        <div className="flex flex-wrap gap-1.5 p-1 bg-slate-100 dark:bg-slate-800 rounded-xl">
          {days.map(d => (
            <button
              key={d}
              onClick={() => setSelectedDay(d)}
              className={`px-3 py-1.5 text-xs font-semibold rounded-lg transition-all ${
                selectedDay === d
                  ? 'bg-primary-600 text-white shadow-sm'
                  : 'text-slate-600 dark:text-slate-400 hover:text-slate-900'
              }`}
            >
              {d}
            </button>
          ))}
        </div>
      </div>

      {/* Schedule Table / Cards */}
      <Card>
        <CardHeader>
          <h3 className="font-semibold text-lg flex items-center gap-2">
            <Calendar className="h-5 w-5 text-primary-600" />
            Weekly Academic Schedule
          </h3>
        </CardHeader>
        <CardContent className="p-0">
          <div className="divide-y divide-slate-100 dark:divide-slate-700">
            {filtered.map((item: any) => (
              <div key={item.id} className="p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4 hover:bg-slate-50 dark:hover:bg-slate-800/40 transition">
                <div className="flex items-start gap-4">
                  <div className="p-3 bg-primary-50 dark:bg-primary-900/30 text-primary-600 rounded-xl text-center min-w-[70px]">
                    <span className="text-xs font-bold block">{item.day.slice(0, 3).toUpperCase()}</span>
                    <span className="text-[10px] text-slate-400 font-mono mt-0.5">{item.start_time}</span>
                  </div>

                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-bold px-2 py-0.5 rounded bg-slate-100 dark:bg-slate-700 font-mono text-primary-600">
                        {item.course_code}
                      </span>
                      <h4 className="font-semibold text-sm text-slate-900 dark:text-white">{item.course_name}</h4>
                    </div>

                    <div className="flex flex-wrap items-center gap-4 text-xs text-slate-400 mt-2">
                      <span className="flex items-center gap-1"><Clock className="h-3.5 w-3.5" /> {item.start_time} – {item.end_time}</span>
                      <span className="flex items-center gap-1"><MapPin className="h-3.5 w-3.5 text-amber-500" /> Room: {item.room_number}</span>
                      <span className="flex items-center gap-1"><User className="h-3.5 w-3.5 text-blue-500" /> {item.faculty_name}</span>
                    </div>
                  </div>
                </div>

                <Badge variant="success">Scheduled</Badge>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
