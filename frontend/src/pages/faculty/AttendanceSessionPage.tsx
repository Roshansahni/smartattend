import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { attendanceService } from '@/services/attendance.service';
import { Card, CardContent, CardHeader } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { formatDateTime } from '@/utils/format';
import { RefreshCw, Play, Square, Users, Clock, ShieldCheck } from 'lucide-react';

export default function AttendanceSessionPage() {
  const { sessionId: courseId } = useParams<{ sessionId: string }>();
  const [active, setActive] = useState(false);
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
  const [qrData, setQrData] = useState<any>(null);
  const [timeLeft, setTimeLeft] = useState(25);
  const [isLoading, setIsLoading] = useState(false);

  // Check if session is already running when page loads
  useEffect(() => {
    if (!courseId) return;
    attendanceService.getCourseStatus(courseId)
      .then(res => {
        if (res.is_active && res.qr) {
          setActive(true);
          setCurrentSessionId(res.session_id);
          setQrData(res.qr);
        }
      })
      .catch(() => {});
  }, [courseId]);

  // Start Session handler
  const handleStartSession = async () => {
    if (!courseId) return;
    setIsLoading(true);
    try {
      const data = await attendanceService.startCourseSession(courseId);
      setActive(true);
      setCurrentSessionId(data.session_id);
      setQrData(data.qr);
      setTimeLeft(25);
      toast.success('Attendance session started! QR code is live.');
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Failed to start attendance session');
    } finally {
      setIsLoading(false);
    }
  };

  // Stop Session handler
  const handleStopSession = async () => {
    if (!courseId) return;
    setIsLoading(true);
    try {
      await attendanceService.endCourseSession(courseId);
      setActive(false);
      setQrData(null);
      toast.success('Attendance session closed.');
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Failed to stop session');
    } finally {
      setIsLoading(false);
    }
  };

  // Rotate QR handler
  const handleRotate = async () => {
    if (!currentSessionId) return;
    try {
      const data = await attendanceService.rotateQR(currentSessionId);
      setQrData(data);
      setTimeLeft(25);
      toast.success('QR Code rotated');
    } catch (err: any) {
      toast.error('Rotation failed');
    }
  };

  // Timer countdown and auto-rotation
  useEffect(() => {
    if (!active || !currentSessionId) return;

    const interval = setInterval(() => {
      setTimeLeft((prev) => {
        if (prev <= 1) {
          handleRotate();
          return 25;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(interval);
  }, [active, currentSessionId]);

  // Live roster query (polls every 4 seconds)
  const { data: records = [] } = useQuery({
    queryKey: ['session-records', currentSessionId],
    queryFn: () => currentSessionId ? attendanceService.getSessionRecords(currentSessionId) : [],
    enabled: active && !!currentSessionId,
    refetchInterval: 4000,
  });

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-2xl font-bold text-slate-900 dark:text-white">Attendance Session Room</h2>
            <Badge variant={active ? 'success' : 'default'}>
              {active ? '● LIVE SESSION' : 'OFFLINE'}
            </Badge>
          </div>
          <p className="text-xs text-slate-500 mt-1 font-mono">Course ID: {courseId}</p>
        </div>

        <div>
          {!active ? (
            <Button
              onClick={handleStartSession}
              isLoading={isLoading}
              className="bg-green-600 hover:bg-green-700"
              leftIcon={<Play className="h-4 w-4" />}
            >
              Start QR Session
            </Button>
          ) : (
            <Button
              onClick={handleStopSession}
              isLoading={isLoading}
              variant="danger"
              leftIcon={<Square className="h-4 w-4" />}
            >
              Stop Session
            </Button>
          )}
        </div>
      </div>

      {/* Main Grid: QR display + Live Roster */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left Column: QR Code Display */}
        <Card className="flex flex-col items-center justify-center p-6 text-center">
          <CardHeader className="w-full text-left p-0 pb-4 border-b">
            <div className="flex items-center justify-between">
              <h3 className="font-semibold text-lg flex items-center gap-2">
                <ShieldCheck className="h-5 w-5 text-primary-600" />
                Dynamic Cryptographic QR
              </h3>
              {active && (
                <span className="text-xs font-mono font-bold text-primary-600 bg-primary-50 px-2.5 py-1 rounded-full flex items-center gap-1">
                  <Clock className="h-3.5 w-3.5 animate-spin" />
                  Rotates in {timeLeft}s
                </span>
              )}
            </div>
          </CardHeader>

          <CardContent className="w-full pt-6 flex flex-col items-center justify-center">
            {active && qrData?.qr_image_base64 ? (
              <div className="space-y-4 animate-fade-in flex flex-col items-center">
                <div className="p-3 bg-white rounded-2xl shadow-md border-2 border-primary-200">
                  <img
                    src={qrData.qr_image_base64}
                    alt="Live Attendance QR Code"
                    className="w-72 h-72 rounded-lg"
                  />
                </div>

                <div className="space-y-1">
                  <p className="text-xs font-semibold text-slate-700 dark:text-slate-300">
                    Students scan using SmartAttend mobile camera
                  </p>
                  <p className="text-[11px] text-slate-400">
                    Token is single-use, expires in 30 seconds to prevent proxy forwarding
                  </p>
                </div>

                <Button
                  size="sm"
                  variant="outline"
                  onClick={handleRotate}
                  leftIcon={<RefreshCw className="h-3.5 w-3.5" />}
                >
                  Force Rotate Now
                </Button>
              </div>
            ) : (
              <div className="py-20 text-center space-y-3">
                <div className="h-16 w-16 bg-slate-100 dark:bg-slate-700 rounded-full flex items-center justify-center mx-auto text-slate-400">
                  <Play className="h-8 w-8 ml-1" />
                </div>
                <h4 className="font-medium text-slate-700 dark:text-slate-300">Session Inactive</h4>
                <p className="text-sm text-slate-400 max-w-sm">
                  Click the green <b>"Start QR Session"</b> button above to generate and project a rotating QR code.
                </p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Right Column: Live Attendance List */}
        <Card className="flex flex-col">
          <CardHeader className="flex flex-row items-center justify-between">
            <h3 className="font-semibold text-lg flex items-center gap-2">
              <Users className="h-5 w-5 text-primary-600" />
              Live Attendance Roster
            </h3>
            <Badge variant="info">{records.length} Present</Badge>
          </CardHeader>

          <CardContent className="flex-1 p-0">
            {records.length > 0 ? (
              <div className="divide-y divide-slate-100 dark:divide-slate-700 max-h-[420px] overflow-y-auto">
                {records.map((r: any) => (
                  <div key={r.record_id} className="px-6 py-3 flex items-center justify-between hover:bg-slate-50 dark:hover:bg-slate-700/30 transition-colors">
                    <div>
                      <p className="font-medium text-sm text-slate-900 dark:text-white">{r.student_name}</p>
                      <p className="text-xs text-slate-400 font-mono">{r.enrollment_number}</p>
                    </div>
                    <div className="text-right">
                      <span className="text-xs text-slate-500 font-mono block">{formatDateTime(r.marked_at)}</span>
                      <span className="text-[10px] text-green-600 font-medium">✓ Verified QR</span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="py-24 text-center text-slate-400 space-y-2">
                <Users className="h-10 w-10 mx-auto text-slate-300 dark:text-slate-600" />
                <p className="text-sm">
                  {active ? 'Waiting for students to scan the live QR code...' : 'No active session running.'}
                </p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
