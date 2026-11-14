import React, { useState, useEffect, useRef } from 'react';
import { Html5Qrcode } from 'html5-qrcode';
import toast from 'react-hot-toast';
import { Camera, MapPin, CheckCircle, XCircle, Upload, Loader2, RefreshCw } from 'lucide-react';
import { attendanceService } from '@/services/attendance.service';
import { Card, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';

export default function ScanQRPage() {
  const [scanning, setScanning] = useState(false);
  const [loadingCamera, setLoadingCamera] = useState(false);
  const [status, setStatus] = useState<'idle' | 'success' | 'error'>('idle');
  const [message, setMessage] = useState('');
  const [coords, setCoords] = useState<{ lat: number; lng: number } | null>(null);
  const scannerRef = useRef<Html5Qrcode | null>(null);
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  useEffect(() => {
    navigator.geolocation?.getCurrentPosition(
      pos => setCoords({ lat: pos.coords.latitude, lng: pos.coords.longitude }),
      () => console.log('Location permission not granted or unavailable')
    );

    return () => {
      if (scannerRef.current) {
        try {
          if (scannerRef.current.isScanning) {
            scannerRef.current.stop().catch(() => {});
          }
        } catch (_) {}
      }
    };
  }, []);

  const handleDecodedToken = async (token: string) => {
    try {
      await attendanceService.markAttendance(token, coords?.lat, coords?.lng);
      setStatus('success');
      setMessage('Attendance marked successfully!');
      toast.success('Attendance recorded');
    } catch (e: any) {
      setStatus('error');
      setMessage(e.response?.data?.detail || 'Verification error or expired token');
      toast.error(e.response?.data?.detail || 'Verification error');
    }
  };

  const startScan = async () => {
    setStatus('idle');
    setLoadingCamera(true);

    try {
      if (scannerRef.current) {
        try {
          if (scannerRef.current.isScanning) {
            await scannerRef.current.stop();
          }
          await scannerRef.current.clear();
        } catch (_) {}
      }

      const scanner = new Html5Qrcode('qr-reader');
      scannerRef.current = scanner;
      const config = { fps: 10, qrbox: { width: 240, height: 240 } };

      try {
        await scanner.start(
          { facingMode: 'environment' },
          config,
          async (token) => {
            try {
              if (scanner.isScanning) {
                await scanner.stop();
              }
            } catch (_) {}
            setScanning(false);
            await handleDecodedToken(token);
          },
          () => {}
        );
      } catch (envErr) {
        console.warn('Environment camera failed, falling back to default camera', envErr);
        await scanner.start(
          { facingMode: 'user' },
          config,
          async (token) => {
            try {
              if (scanner.isScanning) {
                await scanner.stop();
              }
            } catch (_) {}
            setScanning(false);
            await handleDecodedToken(token);
          },
          () => {}
        );
      }

      setScanning(true);
    } catch (err: any) {
      console.error('Camera startup error:', err);
      setScanning(false);
      toast.error(err.message || 'Unable to open camera. You can use "Take Photo / Upload QR" below.');
    } finally {
      setLoadingCamera(false);
    }
  };

  const stopScan = async () => {
    if (scannerRef.current) {
      try {
        if (scannerRef.current.isScanning) {
          await scannerRef.current.stop();
        }
        await scannerRef.current.clear();
      } catch (_) {}
    }
    setScanning(false);
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setStatus('idle');
    const toastId = toast.loading('Reading QR code from photo...');

    try {
      const helperScanner = new Html5Qrcode('qr-file-helper');
      const token = await helperScanner.scanFile(file, false);
      toast.dismiss(toastId);
      await handleDecodedToken(token);
    } catch (err: any) {
      toast.dismiss(toastId);
      setStatus('error');
      setMessage('Could not detect a clear QR code in the image. Please take a closer photo.');
      toast.error('No QR code detected in image');
    } finally {
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  return (
    <div className="max-w-md mx-auto space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-900 dark:text-white">QR Attendance Scanner</h2>
        <p className="text-sm text-slate-500">Scan the live rotating QR code shown by your instructor</p>
      </div>

      <Card>
        <CardContent className="pt-6 text-center space-y-4">
          {status === 'success' && (
            <div className="py-8 space-y-3">
              <CheckCircle className="h-16 w-16 text-green-500 mx-auto" />
              <h3 className="text-lg font-bold text-green-600">Present!</h3>
              <p className="text-sm text-slate-600 dark:text-slate-300">{message}</p>
              <Button onClick={() => setStatus('idle')} variant="outline" className="mt-4">
                Scan Another
              </Button>
            </div>
          )}

          {status === 'error' && (
            <div className="py-8 space-y-3">
              <XCircle className="h-16 w-16 text-red-500 mx-auto" />
              <h3 className="text-lg font-bold text-red-600">Failed</h3>
              <p className="text-sm text-slate-600 dark:text-slate-300">{message}</p>
              <Button onClick={() => setStatus('idle')} variant="outline" className="mt-4">
                Try Again
              </Button>
            </div>
          )}

          {status === 'idle' && (
            <div className="space-y-4">
              {/* Isolated camera preview element */}
              <div
                id="qr-reader"
                className="w-full bg-slate-950 rounded-2xl overflow-hidden min-h-[260px] flex items-center justify-center border border-slate-800"
              />

              {!scanning ? (
                <div className="space-y-2">
                  <Button
                    onClick={startScan}
                    isLoading={loadingCamera}
                    className="w-full"
                    leftIcon={<Camera className="h-4 w-4" />}
                  >
                    Open Live Camera Scanner
                  </Button>

                  <div className="relative py-1">
                    <div className="absolute inset-0 flex items-center"><div className="w-full border-t border-slate-200 dark:border-slate-700" /></div>
                    <div className="relative flex justify-center text-xs uppercase"><span className="bg-white dark:bg-slate-800 px-2 text-slate-400">or</span></div>
                  </div>

                  <input
                    type="file"
                    ref={fileInputRef}
                    accept="image/*"
                    capture="environment"
                    onChange={handleFileUpload}
                    className="hidden"
                  />

                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => fileInputRef.current?.click()}
                    className="w-full"
                    leftIcon={<Upload className="h-4 w-4" />}
                  >
                    Snap Photo / Upload QR Image
                  </Button>
                </div>
              ) : (
                <Button onClick={stopScan} variant="danger" className="w-full">
                  Stop Camera
                </Button>
              )}
            </div>
          )}

          {/* Hidden helper element for file scanning */}
          <div id="qr-file-helper" className="hidden" />
        </CardContent>
      </Card>

      {coords && (
        <div className="text-xs text-slate-500 flex items-center justify-center gap-2 p-2 bg-slate-100 dark:bg-slate-800 rounded-lg">
          <MapPin className="h-4 w-4 text-green-500 shrink-0" />
          <span>GPS Geolocation Ready: {coords.lat.toFixed(4)}, {coords.lng.toFixed(4)}</span>
        </div>
      )}
    </div>
  );
}
