import { api } from './api';
import type { AuthTokens, User } from '@/types';

export const authService = {
  async login(email: string, password: string): Promise<AuthTokens> {
    const { data } = await api.post<AuthTokens>('/auth/login', { email, password });
    return data;
  },
  async getMe(): Promise<User> {
    const { data } = await api.get<User>('/auth/me');
    return data;
  },
  async forgotPassword(email: string) {
    return (await api.post('/auth/forgot-password', { email })).data;
  }
};
