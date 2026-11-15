import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import toast from 'react-hot-toast';
import { Mail, Lock, CalendarCheck } from 'lucide-react';
import { useAuth } from '@/context/AuthContext';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';

const schema = z.object({
  email: z.string().email('Valid email required'),
  password: z.string().min(1, 'Password required'),
});

export default function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<z.infer<typeof schema>>({
    resolver: zodResolver(schema),
  });

  const onSubmit = async (data: z.infer<typeof schema>) => {
    try {
      await login(data.email, data.password);
      toast.success('Logged in successfully');
      setTimeout(() => navigate('/'), 200);
    } catch (err: any) {
      toast.error(err.response?.data?.detail || err.message || 'Authentication failed');
    }
  };

  return (
    <div className="min-h-screen bg-slate-100 dark:bg-slate-900 flex items-center justify-center p-4">
      <div className="w-full max-w-md bg-white dark:bg-slate-800 rounded-2xl shadow-xl p-8 border border-slate-200 dark:border-slate-700">
        <div className="text-center mb-6">
          <div className="inline-flex p-3 bg-primary-600 rounded-xl text-white mb-2">
            <CalendarCheck className="h-8 w-8" />
          </div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">SmartAttend</h1>
          <p className="text-xs text-slate-500 mt-1">Sign in with your institutional account</p>
        </div>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <Input label="Email Address" type="email" leftIcon={<Mail className="h-4 w-4" />} error={errors.email?.message} {...register('email')} />
          <Input label="Password" type="password" leftIcon={<Lock className="h-4 w-4" />} error={errors.password?.message} {...register('password')} />
          <Button type="submit" className="w-full mt-2" isLoading={isSubmitting}>Sign In</Button>
        </form>

        <div className="mt-6 pt-4 border-t border-slate-100 dark:border-slate-700/60 text-center">
          <button
            type="button"
            onClick={() => {
              const current = localStorage.getItem('smartattend_custom_api') || '';
              const newUrl = window.prompt('Configure Backend API Endpoint (e.g. https://...trycloudflare.com/api/v1 or /api/v1):', current);
              if (newUrl !== null) {
                if (newUrl.trim()) {
                  localStorage.setItem('smartattend_custom_api', newUrl.trim());
                  toast.success('Updated Backend API URL');
                } else {
                  localStorage.removeItem('smartattend_custom_api');
                  toast.success('Reset to default API URL');
                }
                window.location.reload();
              }
            }}
            className="text-[11px] text-slate-400 hover:text-primary-600 transition-colors"
          >
            ⚙️ Configure Backend Endpoint
          </button>
        </div>
      </div>
    </div>
  );
}
