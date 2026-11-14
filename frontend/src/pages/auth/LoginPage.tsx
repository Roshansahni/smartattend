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
  const { login, role } = useAuth();
  const navigate = useNavigate();
  const { register, handleSubmit, setValue, formState: { errors, isSubmitting } } = useForm<z.infer<typeof schema>>({
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

  const fillCredentials = (email: string, pass: string) => {
    setValue('email', email, { shouldValidate: true });
    setValue('password', pass, { shouldValidate: true });
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

        <div className="mt-6 p-4 bg-slate-50 dark:bg-slate-700/50 rounded-xl text-xs text-slate-600 dark:text-slate-300 border border-slate-200/60 dark:border-slate-700">
          <p className="font-semibold mb-2 text-slate-900 dark:text-white">⚡ Quick 1-Click Demo Fill:</p>
          <div className="grid grid-cols-2 gap-2">
            <button
              type="button"
              onClick={() => fillCredentials('student1@smartattend.com', 'Student@123')}
              className="p-2 text-left bg-white dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-600 hover:border-primary-500 hover:text-primary-600 transition text-[11px]"
            >
              🎓 <strong>Student</strong>
              <div className="text-[10px] text-slate-400 truncate">student1@smartattend.com</div>
            </button>
            <button
              type="button"
              onClick={() => fillCredentials('faculty@smartattend.com', 'Faculty@123')}
              className="p-2 text-left bg-white dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-600 hover:border-primary-500 hover:text-primary-600 transition text-[11px]"
            >
              👨‍🏫 <strong>Faculty</strong>
              <div className="text-[10px] text-slate-400 truncate">faculty@smartattend.com</div>
            </button>
            <button
              type="button"
              onClick={() => fillCredentials('admin@smartattend.com', 'Admin@123')}
              className="p-2 text-left bg-white dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-600 hover:border-primary-500 hover:text-primary-600 transition text-[11px]"
            >
              🛡️ <strong>Admin</strong>
              <div className="text-[10px] text-slate-400 truncate">admin@smartattend.com</div>
            </button>
            <button
              type="button"
              onClick={() => fillCredentials('superadmin@smartattend.com', 'Admin@123')}
              className="p-2 text-left bg-white dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-600 hover:border-primary-500 hover:text-primary-600 transition text-[11px]"
            >
              ⚙️ <strong>Super Admin</strong>
              <div className="text-[10px] text-slate-400 truncate">superadmin@smartattend.com</div>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
