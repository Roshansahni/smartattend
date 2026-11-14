import React from 'react';
import { Link } from 'react-router-dom';
import { Card, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';

export default function ForgotPasswordPage() {
  return (
    <div className="min-h-screen bg-slate-100 dark:bg-slate-900 flex items-center justify-center p-4">
      <Card className="max-w-md w-full">
        <CardContent className="space-y-4 pt-6">
          <h2 className="text-xl font-bold">Forgot Password</h2>
          <p className="text-sm text-slate-500">Contact your institution administrator to reset your password.</p>
          <Link to="/login"><Button variant="outline" className="w-full">Return to Login</Button></Link>
        </CardContent>
      </Card>
    </div>
  );
}
