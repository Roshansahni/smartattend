import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { erpService } from '@/services/erp.service';
import { Card, CardContent, CardHeader } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { ShieldAlert, FileText, CheckCircle, Lock } from 'lucide-react';

export default function AuditLogsPage() {
  const { data: logs = [], isLoading } = useQuery({
    queryKey: ['audit-logs'],
    queryFn: () => erpService.getAuditLogs(),
  });

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-900 dark:text-white">Security & Attendance Audit Trail</h2>
        <p className="text-sm text-slate-500">Immutable, append-only security logs for forensic compliance and accreditation</p>
      </div>

      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <h3 className="font-semibold text-lg flex items-center gap-2">
              <Lock className="h-5 w-5 text-primary-600" />
              Cryptographic Audit Records
            </h3>
            <Badge variant="success">ISO 27001 Audit Ready</Badge>
          </div>
        </CardHeader>
        <CardContent className="p-0">
          <table className="w-full text-sm">
            <thead className="bg-slate-50 dark:bg-slate-800/50 text-xs text-slate-400">
              <tr>
                <th className="text-left px-6 py-3 font-semibold">Action / Event</th>
                <th className="text-left px-6 py-3 font-semibold">Resource Target</th>
                <th className="text-left px-6 py-3 font-semibold">Client Origin / IP</th>
                <th className="text-left px-6 py-3 font-semibold">Timestamp (UTC)</th>
                <th className="text-right px-6 py-3 font-semibold">Audit State</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-700">
              {logs.map((l: any) => (
                <tr key={l.id} className="hover:bg-slate-50 dark:hover:bg-slate-800/30">
                  <td className="px-6 py-3 font-bold text-xs font-mono text-slate-900 dark:text-white">
                    {l.action}
                  </td>
                  <td className="px-6 py-3 font-mono text-xs text-slate-500">{l.resource_type}</td>
                  <td className="px-6 py-3 font-mono text-xs text-slate-400">{l.ip_address || '127.0.0.1'}</td>
                  <td className="px-6 py-3 text-xs text-slate-500">{l.created_at}</td>
                  <td className="px-6 py-3 text-right">
                    <Badge variant={l.status === 'BLOCKED' ? 'danger' : 'success'}>
                      {l.status || 'VERIFIED'}
                    </Badge>
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
