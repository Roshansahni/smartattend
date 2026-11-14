import React, { useState } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { erpService } from '@/services/erp.service';
import { courseService } from '@/services/course.service';
import { Card, CardContent, CardHeader } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import toast from 'react-hot-toast';
import { HelpCircle, Send, CheckCircle2, Clock, AlertTriangle } from 'lucide-react';

export default function DisputePage() {
  const queryClient = useQueryClient();
  const [courseId, setCourseId] = useState('');
  const [sessionDate, setSessionDate] = useState('');
  const [reason, setReason] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const { data: courses = [] } = useQuery({
    queryKey: ['courses'],
    queryFn: () => courseService.getCourses(),
  });

  const { data: disputes = [] } = useQuery({
    queryKey: ['my-disputes'],
    queryFn: () => erpService.getMyDisputes(),
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!courseId || !sessionDate || !reason) {
      toast.error('Please fill all fields');
      return;
    }
    setIsSubmitting(true);
    try {
      await erpService.createDispute({
        course_id: courseId,
        session_date: sessionDate,
        reason,
      });
      toast.success('Attendance correction request submitted to faculty');
      setReason('');
      setSessionDate('');
      queryClient.invalidateQueries({ queryKey: ['my-disputes'] });
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Failed to submit dispute');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-900 dark:text-white">Attendance Dispute & Correction</h2>
        <p className="text-sm text-slate-500">Request correction for inadvertently missed or erroneously recorded attendance</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card className="lg:col-span-1">
          <CardHeader>
            <h3 className="font-semibold text-lg flex items-center gap-2">
              <HelpCircle className="h-5 w-5 text-primary-600" />
              Submit Request
            </h3>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">Select Course</label>
                <select
                  value={courseId}
                  onChange={(e) => setCourseId(e.target.value)}
                  required
                  className="w-full px-3 py-2 text-sm bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg"
                >
                  <option value="">-- Choose Course --</option>
                  {courses.map(c => (
                    <option key={c.id} value={c.id}>{c.code} - {c.name}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">Lecture Date</label>
                <input
                  type="date"
                  value={sessionDate}
                  onChange={(e) => setSessionDate(e.target.value)}
                  required
                  className="w-full px-3 py-2 text-xs bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">Reason / Justification</label>
                <textarea
                  rows={3}
                  value={reason}
                  onChange={(e) => setReason(e.target.value)}
                  placeholder="e.g. Scanned QR code but cellular network dropped before sync confirmation..."
                  required
                  className="w-full px-3 py-2 text-sm bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg"
                />
              </div>

              <Button type="submit" isLoading={isSubmitting} className="w-full" leftIcon={<Send className="h-4 w-4" />}>
                Submit for Faculty Review
              </Button>
            </form>
          </CardContent>
        </Card>

        <Card className="lg:col-span-2">
          <CardHeader>
            <h3 className="font-semibold text-lg flex items-center gap-2">
              <Clock className="h-5 w-5 text-primary-600" />
              Correction Requests
            </h3>
          </CardHeader>
          <CardContent className="p-0">
            {disputes.length > 0 ? (
              <div className="divide-y divide-slate-100 dark:divide-slate-700">
                {disputes.map((d: any) => (
                  <div key={d.id} className="p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-xs bg-primary-50 text-primary-600 px-2 py-0.5 rounded font-mono">{d.course_code}</span>
                        <span className="font-semibold text-sm">{d.course_name}</span>
                        <Badge variant={d.status === 'resolved' ? 'success' : d.status === 'rejected' ? 'danger' : 'warning'}>
                          {d.status.toUpperCase()}
                        </Badge>
                      </div>
                      <p className="text-xs text-slate-500 mt-1">Class Date: {d.session_date}</p>
                      <p className="text-xs text-slate-600 dark:text-slate-300 mt-1 italic">"{d.reason}"</p>
                      {d.faculty_response && (
                        <p className="text-xs text-primary-600 mt-1 font-medium">Instructor response: {d.faculty_response}</p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="py-16 text-center text-slate-400">
                <CheckCircle2 className="h-10 w-10 mx-auto text-green-500 mb-2" />
                <p className="text-sm">No attendance disputes submitted.</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
