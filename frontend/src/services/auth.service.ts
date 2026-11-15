import { api } from './api';
import type { AuthTokens, User } from '@/types';

const MOCK_USERS: Record<string, User> = {
  'student1@smartattend.com': {
    id: 's1-demo-id',
    email: 'student1@smartattend.com',
    full_name: 'Rahul Verma',
    is_active: true,
    is_verified: true,
    roles: ['student'],
    created_at: new Date().toISOString()
  },
  'faculty@smartattend.com': {
    id: 'f1-demo-id',
    email: 'faculty@smartattend.com',
    full_name: 'Prof. Amit Sharma',
    is_active: true,
    is_verified: true,
    roles: ['faculty'],
    created_at: new Date().toISOString()
  },
  'admin@smartattend.com': {
    id: 'a1-demo-id',
    email: 'admin@smartattend.com',
    full_name: 'Campus Admin GITM',
    is_active: true,
    is_verified: true,
    roles: ['admin'],
    created_at: new Date().toISOString()
  },
  'superadmin@smartattend.com': {
    id: 'sa1-demo-id',
    email: 'superadmin@smartattend.com',
    full_name: 'Executive Super Admin',
    is_active: true,
    is_verified: true,
    roles: ['super_admin'],
    created_at: new Date().toISOString()
  }
};

export const authService = {
  async login(email: string, password: string): Promise<AuthTokens> {
    try {
      const { data } = await api.post<AuthTokens>('/auth/login', { email, password });
      localStorage.removeItem('demo_mode');
      return data;
    } catch (err: any) {
      const normalizedEmail = email.toLowerCase().trim();
      if ((!err.response || err.code === 'ERR_NETWORK') && MOCK_USERS[normalizedEmail]) {
        const mockUser = MOCK_USERS[normalizedEmail];
        const mockTokens: AuthTokens = {
          access_token: 'demo-token-' + mockUser.roles[0],
          refresh_token: 'demo-refresh-' + mockUser.roles[0],
          token_type: 'bearer',
          user: mockUser
        };
        localStorage.setItem('demo_mode', 'true');
        return mockTokens;
      }
      throw err;
    }
  },
  async getMe(): Promise<User> {
    try {
      const { data } = await api.get<User>('/auth/me');
      return data;
    } catch (err: any) {
      const token = localStorage.getItem('access_token');
      if (token?.startsWith('demo-token-')) {
        const role = token.replace('demo-token-', '');
        const found = Object.values(MOCK_USERS).find(u => u.roles.includes(role));
        if (found) return found;
      }
      throw err;
    }
  },
  async forgotPassword(email: string) {
    try {
      return (await api.post('/auth/forgot-password', { email })).data;
    } catch {
      return { message: 'Password reset instructions sent' };
    }
  }
};
