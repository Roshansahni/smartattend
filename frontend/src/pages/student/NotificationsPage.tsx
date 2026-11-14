import React from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { erpService } from '@/services/erp.service';
import { Card, CardContent, CardHeader } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import toast from 'react-hot-toast';
import { Bell, AlertTriangle, CheckCircle, Info, Check } from 'lucide-react';

export default function NotificationsPage() {
  const queryClient = useQueryClient();

  const { data: notifications = [], isLoading } = useQuery({
    queryKey: ['notifications'],
    queryFn: () => erpService.getNotifications(),
  });

  const markReadMutation = useMutation({
    mutationFn: (id: string) => erpService.markNotificationRead(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications'] });
    },
  });

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-slate-900 dark:text-white">Academic Notifications</h2>
          <p className="text-sm text-slate-500">Real-time attendance warnings, timetable updates, and departmental notices</p>
        </div>
      </div>

      <Card>
        <CardHeader>
          <h3 className="font-semibold text-lg flex items-center gap-2">
            <Bell className="h-5 w-5 text-primary-600" />
            Notification Center ({notifications.filter((n: any) => !n.is_read).length} unread)
          </h3>
        </CardHeader>
        <CardContent className="p-0">
          <div className="divide-y divide-slate-100 dark:divide-slate-700">
            {notifications.map((n: any) => (
              <div
                key={n.id}
                className={`p-4 flex items-start justify-between gap-4 transition ${
                  n.is_read ? 'opacity-70 bg-white dark:bg-slate-800' : 'bg-primary-50/30 dark:bg-primary-950/20'
                }`}
              >
                <div className="flex items-start gap-3">
                  <div className="mt-0.5">
                    {n.type === 'warning' ? (
                      <AlertTriangle className="h-5 w-5 text-amber-500" />
                    ) : n.type === 'success' ? (
                      <CheckCircle className="h-5 w-5 text-green-500" />
                    ) : (
                      <Info className="h-5 w-5 text-blue-500" />
                    )}
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <h4 className="font-semibold text-sm text-slate-900 dark:text-white">{n.title}</h4>
                      {!n.is_read && <span className="h-2 w-2 rounded-full bg-primary-600 inline-block" />}
                    </div>
                    <p className="text-xs text-slate-600 dark:text-slate-300 mt-1">{n.message}</p>
                    <span className="text-[11px] text-slate-400 mt-2 block font-mono">
                      {new Date(n.created_at).toLocaleDateString()}
                    </span>
                  </div>
                </div>

                {!n.is_read && (
                  <Button
                    size="sm"
                    variant="outline"
                    className="shrink-0 text-xs"
                    onClick={() => markReadMutation.mutate(n.id)}
                    leftIcon={<Check className="h-3 w-3" />}
                  >
                    Mark Read
                  </Button>
                )}
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
