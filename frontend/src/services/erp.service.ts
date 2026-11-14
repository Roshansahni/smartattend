import { api } from './api';

export const erpService = {
  // Leave
  async getMyLeaveApplications() {
    return (await api.get('/leave/my-applications')).data;
  },
  async applyLeave(data: { leave_type: string; start_date: string; end_date: string; reason: string }) {
    return (await api.post('/leave/apply', data)).data;
  },
  async getPendingLeaves() {
    return (await api.get('/leave/pending-reviews')).data;
  },
  async reviewLeave(id: string, data: { status: string; remarks?: string }) {
    return (await api.put(`/leave/${id}/review`, data)).data;
  },

  // Timetable
  async getTimetable(params?: { day?: string; semester?: number }) {
    return (await api.get('/timetable', { params })).data;
  },
  async createTimetableEntry(data: any) {
    return (await api.post('/timetable', data)).data;
  },

  // Disputes
  async getMyDisputes() {
    return (await api.get('/disputes/my-disputes')).data;
  },
  async createDispute(data: { course_id: string; session_date: string; reason: string }) {
    return (await api.post('/disputes', data)).data;
  },
  async getPendingDisputes() {
    return (await api.get('/disputes/pending')).data;
  },
  async resolveDispute(id: string, data: { status: string; response?: string }) {
    return (await api.put(`/disputes/${id}/resolve`, data)).data;
  },

  // Notifications
  async getNotifications() {
    return (await api.get('/notifications')).data;
  },
  async markNotificationRead(id: string) {
    return (await api.put(`/notifications/${id}/read`)).data;
  },

  // Analytics & AI Prediction
  async getAiPredictions() {
    return (await api.get('/analytics/ai-prediction')).data;
  },
  async getDepartmentComparison() {
    return (await api.get('/analytics/department-comparison')).data;
  },
  async getAuditLogs() {
    return (await api.get('/analytics/audit-logs')).data;
  },
  async getSystemConfig() {
    return (await api.get('/analytics/system-config')).data;
  },
};
