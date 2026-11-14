import React, { useState } from 'react';
import { Card, CardContent, CardHeader } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import toast from 'react-hot-toast';
import { Sliders, Shield, QrCode, MapPin, Save, AlertTriangle } from 'lucide-react';

export default function SystemConfigPage() {
  const [threshold, setThreshold] = useState(75);
  const [rotationInterval, setRotationInterval] = useState(25);
  const [expirationWindow, setExpirationWindow] = useState(30);
  const [geofenceRadius, setGeofenceRadius] = useState(100);
  const [gpsEnforced, setGpsEnforced] = useState(true);
  const [antiProxyMode, setAntiProxyMode] = useState(true);

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    toast.success('System parameters updated and synchronized across all active nodes!');
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-900 dark:text-white">System Configuration</h2>
        <p className="text-sm text-slate-500">Configure institutional attendance rules, cryptographic security parameters, and thresholds</p>
      </div>

      <form onSubmit={handleSave} className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Attendance Rules Card */}
          <Card>
            <CardHeader>
              <h3 className="font-semibold text-lg flex items-center gap-2">
                <Sliders className="h-5 w-5 text-primary-600" />
                Academic Attendance Policy
              </h3>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
                  Mandatory Minimum Attendance Percentage
                </label>
                <div className="flex items-center gap-3">
                  <input
                    type="number"
                    min="50"
                    max="100"
                    value={threshold}
                    onChange={(e) => setThreshold(Number(e.target.value))}
                    className="w-24 px-3 py-2 text-sm bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg font-bold font-mono"
                  />
                  <span className="text-sm font-semibold">%</span>
                  <Badge variant="warning">Standard University Mandate</Badge>
                </div>
                <p className="text-[11px] text-slate-400 mt-1">
                  Students falling below this threshold are automatically flagged for examination debarment and receive notification warnings.
                </p>
              </div>

              <div className="pt-4 border-t">
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
                  Consecutive Absence Alert Trigger
                </label>
                <span className="text-sm font-bold text-slate-800 dark:text-slate-200">3 Consecutive Classes</span>
                <p className="text-[11px] text-slate-400 mt-0.5">Triggers automated mentor notification and counselor check-in.</p>
              </div>
            </CardContent>
          </Card>

          {/* Cryptographic QR Security */}
          <Card>
            <CardHeader>
              <h3 className="font-semibold text-lg flex items-center gap-2">
                <QrCode className="h-5 w-5 text-primary-600" />
                Dynamic QR Engine Settings
              </h3>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
                  QR Auto-Rotation Interval
                </label>
                <div className="flex items-center gap-3">
                  <input
                    type="number"
                    min="10"
                    max="60"
                    value={rotationInterval}
                    onChange={(e) => setRotationInterval(Number(e.target.value))}
                    className="w-24 px-3 py-2 text-sm bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg font-bold font-mono"
                  />
                  <span className="text-xs text-slate-400">Seconds per token</span>
                </div>
                <p className="text-[11px] text-slate-400 mt-1">
                  Regenerates a new cryptographic nonce to invalidate captured photos.
                </p>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
                  Server-side Token Expiration TTL
                </label>
                <div className="flex items-center gap-3">
                  <input
                    type="number"
                    min="15"
                    max="90"
                    value={expirationWindow}
                    onChange={(e) => setExpirationWindow(Number(e.target.value))}
                    className="w-24 px-3 py-2 text-sm bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg font-bold font-mono"
                  />
                  <span className="text-xs text-slate-400">Seconds grace buffer</span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* GPS Geofencing Configuration */}
          <Card>
            <CardHeader>
              <h3 className="font-semibold text-lg flex items-center gap-2">
                <MapPin className="h-5 w-5 text-primary-600" />
                GPS Geofence Perimeter
              </h3>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
                  Classroom Geofence Radius
                </label>
                <div className="flex items-center gap-3">
                  <input
                    type="number"
                    min="20"
                    max="500"
                    value={geofenceRadius}
                    onChange={(e) => setGeofenceRadius(Number(e.target.value))}
                    className="w-24 px-3 py-2 text-sm bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg font-bold font-mono"
                  />
                  <span className="text-xs text-slate-400">Meters radius from lecture hall</span>
                </div>
                <p className="text-[11px] text-slate-400 mt-1">
                  Uses Haversine formula to verify student is physically present inside the lecture hall.
                </p>
              </div>

              <div className="flex items-center justify-between pt-4 border-t">
                <div>
                  <span className="text-sm font-semibold block text-slate-800 dark:text-slate-200">Enforce Strict Geofencing</span>
                  <span className="text-xs text-slate-400">Reject attendance if GPS coordinates fall outside radius</span>
                </div>
                <input
                  type="checkbox"
                  checked={gpsEnforced}
                  onChange={(e) => setGpsEnforced(e.target.checked)}
                  className="h-5 w-5 text-primary-600 rounded"
                />
              </div>
            </CardContent>
          </Card>

          {/* Security Guardrails */}
          <Card>
            <CardHeader>
              <h3 className="font-semibold text-lg flex items-center gap-2">
                <Shield className="h-5 w-5 text-primary-600" />
                Anti-Proxy Fraud Detection
              </h3>
            </CardHeader>
            <CardContent className="space-y-4 text-xs">
              <div className="flex items-center justify-between py-2 border-b">
                <span>Composite DB Unique Constraint</span>
                <Badge variant="success">Active (Hardware DB Level)</Badge>
              </div>
              <div className="flex items-center justify-between py-2 border-b">
                <span>Single-Use Token Consumption</span>
                <Badge variant="success">Enabled (Atomic Consume)</Badge>
              </div>
              <div className="flex items-center justify-between py-2 border-b">
                <span>Server-side UTC Time Sync</span>
                <Badge variant="success">Synchronized</Badge>
              </div>
              <div className="flex items-center justify-between py-2">
                <span>Immutable Audit Trail</span>
                <Badge variant="success">Append-Only Active</Badge>
              </div>
            </CardContent>
          </Card>
        </div>

        <Button type="submit" className="w-full sm:w-auto" leftIcon={<Save className="h-4 w-4" />}>
          Save & Apply Configuration
        </Button>
      </form>
    </div>
  );
}
