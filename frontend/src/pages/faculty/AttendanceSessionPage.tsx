import React, { useState } from 'react';
import { useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { attendanceService } from '@/services/attendance.service';
import { Card, CardContent, CardHeader } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { formatDateTime } from '@/utils/format';

export default function AttendanceSessionPage() {
  const { sessionId } = useParams<{ sessionId: string }>();
  const [active, setActive] = useState(false);

  const { data: qrData, refetch } = useQuery({
    queryKey: ['qr', sessionId],
    queryFn: () => attendanceService.getQRCode(sessionId!),
    enabled: active,
    refetchInterval: 25000,
  });

  const { data: records = [] } = useQuery({
    queryKey: ['session-records', sessionId],
    queryFn: () => attendanceService.getSessionRecords(sessionId!),
    enabled: active,
    refetchInterval: 5000,
  });

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold">Attendance Session Room</h2>
          <p className="text-sm text-slate-500">Session ID: {sessionId}</p>
        </div>
        <Button variant={active ? 'danger' : 'primary'} onClick={() => setActive(!active)}>
          {active ? 'Stop Session' : 'Start QR Session'}
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader><h3 className="font-semibold">Dynamic QR Display</h3></CardHeader>
          <CardContent className="text-center">
            {active && qrData ? (
              <div className="space-y-4">
                <img src={qrData.qr_image_base64} alt="QR Code" className="mx-auto w-64 h-64 border p-2 rounded-xl" />
                <p className="text-xs text-slate-400">Auto-rotates every 25 seconds</p>
                <Button size="sm" variant="outline" onClick={() => refetch()}>Force Rotate</Button>
              </div>
            ) : (
              <div className="py-16 text-slate-400 text-sm">
                Click "Start QR Session" to generate live QR code for students to scan.
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <div className="flex justify-between items-center">
              <h3 className="font-semibold">Live Attendance Roster</h3>
              <Badge variant="info">{records.length} Present</Badge>
            </div>
          </CardHeader>
          <CardContent>
            {records.length > 0 ? (
              <div className="divide-y divide-slate-100 dark:divide-slate-700 max-h-80 overflow-y-auto">
                {records.map(r => (
                  <div key={r.record_id} className="py-2 flex justify-between items-center text-sm">
                    <div>
                      <p className="font-medium">{r.student_name}</p>
                      <p className="text-xs text-slate-400">{r.enrollment_number}</p>
                    </div>
                    <span className="text-xs text-slate-400">{formatDateTime(r.marked_at)}</span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-slate-400 text-center py-12">Waiting for students to scan...</p>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
