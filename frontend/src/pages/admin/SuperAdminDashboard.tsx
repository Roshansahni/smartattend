import React from 'react';
import { Card, CardContent, CardHeader } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Shield, Building, Globe, Users, Key, Server, Lock } from 'lucide-react';
import toast from 'react-hot-toast';

export default function SuperAdminDashboard() {
  const campuses = [
    { name: 'Main Campus (North Wing)', city: 'New Delhi', students: 2450, faculty: 180, status: 'Active' },
    { name: 'City Engineering Campus', city: 'Gurugram', students: 1620, faculty: 120, status: 'Active' },
    { name: 'Research & Innovation Tech Park', city: 'Noida', students: 840, faculty: 65, status: 'Active' },
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between sm:items-center gap-4">
        <div>
          <h2 className="text-2xl font-bold text-slate-900 dark:text-white">Super Admin Command Center</h2>
          <p className="text-sm text-slate-500">Multi-campus governance, institutional administrators & enterprise security</p>
        </div>
        <Badge variant="success">Multi-Tenant Cloud ERP Mode</Badge>
      </div>

      {/* Campuses Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {campuses.map((c, idx) => (
          <Card key={idx} className="hover:shadow-lg transition">
            <CardHeader>
              <div className="flex items-center justify-between">
                <Badge variant="info">{c.city}</Badge>
                <Badge variant="success">{c.status}</Badge>
              </div>
              <h3 className="font-bold text-lg mt-2 text-slate-900 dark:text-white">{c.name}</h3>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-2 text-xs pt-2 border-t">
                <div className="p-2 bg-slate-50 dark:bg-slate-800 rounded-lg">
                  <span className="text-slate-400 block font-medium">Students</span>
                  <span className="text-base font-bold text-slate-900 dark:text-white">{c.students}</span>
                </div>
                <div className="p-2 bg-slate-50 dark:bg-slate-800 rounded-lg">
                  <span className="text-slate-400 block font-medium">Faculty Staff</span>
                  <span className="text-base font-bold text-slate-900 dark:text-white">{c.faculty}</span>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Enterprise Security Settings */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <h3 className="font-semibold text-lg flex items-center gap-2">
              <Lock className="h-5 w-5 text-primary-600" />
              Institutional Security Policies
            </h3>
          </CardHeader>
          <CardContent className="space-y-3 text-xs">
            <div className="flex justify-between py-2 border-b">
              <span>JWT Authentication Signing:</span>
              <span className="font-mono font-bold text-primary-600">HMAC-SHA256 (256-bit)</span>
            </div>
            <div className="flex justify-between py-2 border-b">
              <span>Session Inactivity Expiration:</span>
              <span className="font-mono">30 Minutes</span>
            </div>
            <div className="flex justify-between py-2 border-b">
              <span>Password Hashing Algorithm:</span>
              <span className="font-mono font-bold text-green-600">bcrypt (Cost Factor 12)</span>
            </div>
            <div className="flex justify-between py-2 border-b">
              <span>Geo-fencing Perimeter Check:</span>
              <span className="font-mono text-green-600">Haversine Great-Circle Distance</span>
            </div>
            <div className="flex justify-between py-2">
              <span>Disaster Recovery Backup:</span>
              <span className="font-mono text-green-600">Automated Daily Snapshot</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <h3 className="font-semibold text-lg flex items-center gap-2">
              <Server className="h-5 w-5 text-primary-600" />
              ERP System Health
            </h3>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="p-3 bg-green-50 dark:bg-green-950/30 border border-green-200 dark:border-green-800 rounded-xl flex items-center gap-3">
              <div className="h-3 w-3 rounded-full bg-green-500 animate-pulse" />
              <div className="text-xs text-green-800 dark:text-green-300">
                <span className="font-bold block">All Microservices Healthy</span>
                API Gateway, QR Rotation Daemon & Database connections running at 99.98% uptime.
              </div>
            </div>
            <div className="grid grid-cols-2 gap-2 text-xs">
              <div className="p-3 bg-slate-50 dark:bg-slate-800 rounded-lg">
                <span className="text-slate-400 block">Active Tunnels</span>
                <span className="text-base font-bold text-primary-600">Cloudflare Edge</span>
              </div>
              <div className="p-3 bg-slate-50 dark:bg-slate-800 rounded-lg">
                <span className="text-slate-400 block">Database Latency</span>
                <span className="text-base font-bold text-green-600">0.8 ms</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
