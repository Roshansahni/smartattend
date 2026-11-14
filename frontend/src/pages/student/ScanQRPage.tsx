import React, { useState, useEffect, useRef } from 'react';
import { Html5Qrcode } from 'html5-qrcode';
import toast from 'react-hot-toast';
import { Camera, MapPin, CheckCircle, XCircle } from 'lucide-react';
import { attendanceService } from '@/services/attendance.service';
import { Card, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';

export default function ScanQRPage() {
  const [scanning, setScanning] = useState(false);
  const [status, setStatus] = useState<'idle' | 'success' | 'error'>('idle');
  const [message, setMessage] = useState('');
  const [coords, setCoords] = useState<{ lat: number; lng: number } | null>(null);
  const scannerRef = useRef<Html5Qrcode | null>(null);

  useEffect(() => {
    navigator.geolocation?.getCurrentPosition(
      pos => setCoords({ lat: pos.coords.latitude, lng: pos.coords.longitude }),
      err => console.log('Location not granted')
    );
  }, []);

  const startScan = async () => {
    setStatus('idle');
    try {
      const scanner = new Html5Qrcode('qr-box');
      scannerRef.current = scanner;
      setScanning(true);
      await scanner.start(
        { facingMode: 'environment' },
        { fps: 10, qrbox: { width: 250, height: 250 } },
        async (token) => {
          await scanner.stop();
          setScanning(false);
          try {
            await attendanceService.markAttendance(token, coords?.lat, coords?.lng);
            setStatus('success');
            setMessage('Attendance marked successfully!');
            toast.success('Attendance recorded');
          } catch (e: any) {
            setStatus('error');
            setMessage(e.response?.data?.detail || 'Failed to mark attendance');
            toast.error(e.response?.data?.detail || 'Verification error');
          }
        },
        () => {}
      );
    } catch {
      setScanning(false);
      toast.error('Unable to access camera.');
    }
  };

  const stopScan = async () => {
    if (scannerRef.current && scanning) {
      await scannerRef.current.stop();
      setScanning(false);
    }
  };

  return (
    <div className="max-w-md mx-auto space-y-6">
      <div>
        <h2 className="text-2xl font-bold">QR Attendance Scanner</h2>
        <p className="text-sm text-slate-500">Scan the live QR code presented by your instructor</p>
      </div>

      <Card>
        <CardContent className="pt-6 text-center">
          {status === 'success' && (
            <div className="py-8">
              <CheckCircle className="h-14 w-14 text-green-500 mx-auto mb-3" />
              <p className="font-semibold text-green-600">{message}</p>
            </div>
          )}
          {status === 'error' && (
            <div className="py-8">
              <XCircle className="h-14 w-14 text-red-500 mx-auto mb-3" />
              <p className="font-semibold text-red-600">{message}</p>
              <Button onClick={() => setStatus('idle')} variant="outline" className="mt-4">Retry</Button>
            </div>
          )}
          {status === 'idle' && (
            <div>
              <div id="qr-box" className="w-full rounded-lg overflow-hidden bg-slate-100 dark:bg-slate-700 min-h-[260px] flex items-center justify-center">
                {!scanning && <Camera className="h-12 w-12 text-slate-400" />}
              </div>
              <div className="mt-4">
                {!scanning ? (
                  <Button onClick={startScan} className="w-full" leftIcon={<Camera className="h-4 w-4" />}>Start Scanner</Button>
                ) : (
                  <Button onClick={stopScan} variant="danger" className="w-full">Stop Camera</Button>
                )}
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {coords && (
        <div className="text-xs text-slate-500 flex items-center gap-2 px-2">
          <MapPin className="h-3.5 w-3.5 text-green-500" />
          <span>GPS ready: {coords.lat.toFixed(4)}, {coords.lng.toFixed(4)}</span>
        </div>
      )}
    </div>
  );
}
