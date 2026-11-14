import { api } from './api';

export const analyticsService = {
  async getDashboardStats() {
    const { data } = await api.get('/analytics/dashboard');
    return data;
  }
};
