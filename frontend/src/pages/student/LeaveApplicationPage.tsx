import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { erpService } from '@/services/erp.service';
import { Card, CardContent, CardHeader } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Badge } from '@/components/ui/Badge';
import toast from 'react-hot-toast';
import { FileText, Send, Clock, CheckCircle2, XCircle } from 'lucide-react';

export default function LeaveApplicationPage() {
  const queryClient = useQueryClient();
  const [leaveType, setLeaveType] = useState('medical');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [reason, setReason] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const { data: applications = [], isLoading } = useQuery({
    queryKey: ['my-leaves'],
    queryFn: () => erpService.getMyLeaveApplications(),
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!startDate || !endDate || !reason) {
      toast.error('Please fill all required fields');
      return;
    }
    setIsSubmitting(true);
    try {
      await erpService.applyLeave({
        leave_type: leaveType,
        start_date: startDate,
        end_date: endDate,
        reason,
      });
      toast.success('Leave application submitted for approval');
      setReason('');
      setStartDate('');
      setEndDate('');
      queryClient.invalidateQueries({ queryKey: ['my-leaves'] });
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Failed to submit leave request');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-900 dark:text-white">Leave Application</h2>
        <p className="text-sm text-slate-500">Apply for medical, casual, or academic leave and monitor approval status</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Form */}
        <Card className="lg:col-span-1">
          <CardHeader>
            <h3 className="font-semibold text-lg flex items-center gap-2">
              <FileText className="h-5 w-5 text-primary-600" />
              Apply for Leave
            </h3>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">Leave Type</label>
                <select
                  value={leaveType}
                  onChange={(e) => setLeaveType(e.target.value)}
                  className="w-full px-3 py-2 text-sm bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                >
                  <option value="medical">🏥 Medical Leave</option>
                  <option value="casual">🌴 Casual Leave</option>
                  <option value="academic">🎓 Academic / Duty Leave</option>
                </select>
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">Start Date</label>
                  <input
                    type="date"
                    value={startDate}
                    onChange={(e) => setStartDate(e.target.value)}
                    required
                    className="w-full px-3 py-2 text-xs bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">End Date</label>
                  <input
                    type="date"
                    value={endDate}
                    onChange={(e) => setEndDate(e.target.value)}
                    required
                    className="w-full px-3 py-2 text-xs bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">Reason / Explanation</label>
                <textarea
                  rows={3}
                  value={reason}
                  onChange={(e) => setReason(e.target.value)}
                  placeholder="Provide clinical diagnosis or formal justification..."
                  required
                  className="w-full px-3 py-2 text-sm bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
              </div>

              <Button type="submit" isLoading={isSubmitting} className="w-full" leftIcon={<Send className="h-4 w-4" />}>
                Submit Application
              </Button>
            </form>
          </CardContent>
        </Card>

        {/* Right Column: History */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <h3 className="font-semibold text-lg flex items-center gap-2">
              <Clock className="h-5 w-5 text-primary-600" />
              Application History
            </h3>
          </CardHeader>
          <CardContent className="p-0">
            {applications.length > 0 ? (
              <div className="divide-y divide-slate-100 dark:divide-slate-700">
                {applications.map((app: any) => (
                  <div key={app.id} className="p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-semibold text-sm text-slate-900 dark:text-white">{app.leave_type} LEAVE</span>
                        <Badge
                          variant={
                            app.status.toLowerCase() === 'approved'
                              ? 'success'
                              : app.status.toLowerCase() === 'rejected'
                              ? 'danger'
                              : 'warning'
                          }
                        >
                          {app.status.toUpperCase()}
                        </Badge>
                      </div>
                      <p className="text-xs text-slate-500 mt-1">Duration: {app.start_date} to {app.end_date}</p>
                      <p className="text-xs text-slate-600 dark:text-slate-300 mt-1 italic">"{app.reason}"</p>
                      {app.faculty_remarks && (
                        <p className="text-xs text-primary-600 mt-1 font-medium">Faculty note: {app.faculty_remarks}</p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="py-16 text-center text-slate-400">
                <FileText className="h-10 w-10 mx-auto text-slate-300 mb-2" />
                <p className="text-sm">No leave applications submitted yet.</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
