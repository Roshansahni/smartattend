import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { erpService } from '@/services/erp.service';
import { Card, CardContent, CardHeader } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import toast from 'react-hot-toast';
import { CheckCircle2, XCircle, Clock, FileText, Check, X } from 'lucide-react';

export default function LeaveApprovalPage() {
  const queryClient = useQueryClient();
  const [remarks, setRemarks] = useState<Record<string, string>>({});

  const { data: leaves = [], isLoading } = useQuery({
    queryKey: ['pending-leaves'],
    queryFn: () => erpService.getPendingLeaves(),
  });

  const reviewMutation = useMutation({
    mutationFn: ({ id, status, remark }: { id: string; status: string; remark?: string }) =>
      erpService.reviewLeave(id, { status, remarks: remark }),
    onSuccess: (_, vars) => {
      toast.success(`Leave application ${vars.status} successfully`);
      queryClient.invalidateQueries({ queryKey: ['pending-leaves'] });
    },
    onError: () => toast.error('Failed to update leave status'),
  });

  const handleAction = (id: string, status: 'approved' | 'rejected') => {
    reviewMutation.mutate({
      id,
      status,
      remark: remarks[id] || (status === 'approved' ? 'Leave Approved' : 'Insufficient Justification'),
    });
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-900 dark:text-white">Student Leave Approvals</h2>
        <p className="text-sm text-slate-500">Review student medical, casual, and academic duty leave requests</p>
      </div>

      <Card>
        <CardHeader>
          <h3 className="font-semibold text-lg flex items-center gap-2">
            <Clock className="h-5 w-5 text-primary-600" />
            Submitted Applications ({leaves.length})
          </h3>
        </CardHeader>
        <CardContent className="p-0">
          {leaves.length > 0 ? (
            <div className="divide-y divide-slate-100 dark:divide-slate-700">
              {leaves.map((l: any) => (
                <div key={l.id} className="p-6 flex flex-col lg:flex-row lg:items-center justify-between gap-4">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="font-bold text-slate-900 dark:text-white">{l.student_name}</span>
                      <span className="text-xs font-mono text-slate-400">({l.enrollment_number})</span>
                      <Badge variant="info">{l.leave_type}</Badge>
                      <Badge
                        variant={
                          l.status.toLowerCase() === 'approved'
                            ? 'success'
                            : l.status.toLowerCase() === 'rejected'
                            ? 'danger'
                            : 'warning'
                        }
                      >
                        {l.status.toUpperCase()}
                      </Badge>
                    </div>

                    <p className="text-xs text-slate-500">
                      Dates: <b>{l.start_date}</b> to <b>{l.end_date}</b>
                    </p>
                    <p className="text-xs text-slate-600 dark:text-slate-300 italic bg-slate-50 dark:bg-slate-800 p-2.5 rounded-lg max-w-xl">
                      "{l.reason}"
                    </p>
                  </div>

                  <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2">
                    <input
                      type="text"
                      placeholder="Add instructor remark..."
                      value={remarks[l.id] || ''}
                      onChange={(e) => setRemarks({ ...remarks, [l.id]: e.target.value })}
                      className="px-3 py-1.5 text-xs bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg min-w-[200px]"
                    />
                    <div className="flex gap-2">
                      <Button
                        size="sm"
                        onClick={() => handleAction(l.id, 'approved')}
                        className="bg-green-600 hover:bg-green-700 text-xs flex items-center gap-1"
                      >
                        <Check className="h-3.5 w-3.5" /> Approve
                      </Button>
                      <Button
                        size="sm"
                        variant="danger"
                        onClick={() => handleAction(l.id, 'rejected')}
                        className="text-xs flex items-center gap-1"
                      >
                        <X className="h-3.5 w-3.5" /> Reject
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="py-16 text-center text-slate-400">
              <CheckCircle2 className="h-10 w-10 mx-auto text-green-500 mb-2" />
              <p className="text-sm">All student leave applications are reviewed.</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
