import { api } from './api';
import type { AttendanceSession, QRTokenData, AttendanceRecord, LiveAttendanceRecord } from '@/types';

export const attendanceService = {
  async startCourseSession(courseId: string) {
    return (await api.post(`/attendance/course/${courseId}/start`)).data;
  },
  async endCourseSession(courseId: string) {
    return (await api.post(`/attendance/course/${courseId}/end`)).data;
  },
  async getCourseStatus(courseId: string) {
    return (await api.get(`/attendance/course/${courseId}/status`)).data;
  },
  async createSession(data: any): Promise<AttendanceSession> {
    return (await api.post<AttendanceSession>('/attendance/sessions', data)).data;
  },
  async startSession(sessionId: string): Promise<AttendanceSession> {
    return (await api.post<AttendanceSession>(`/attendance/sessions/${sessionId}/start`)).data;
  },
  async endSession(sessionId: string): Promise<AttendanceSession> {
    return (await api.post<AttendanceSession>(`/attendance/sessions/${sessionId}/end`)).data;
  },
  async getQRCode(sessionId: string): Promise<QRTokenData> {
    return (await api.get<QRTokenData>(`/attendance/sessions/${sessionId}/qr`)).data;
  },
  async rotateQR(sessionId: string): Promise<QRTokenData> {
    return (await api.post<QRTokenData>(`/attendance/sessions/${sessionId}/qr/rotate`)).data;
  },
  async markAttendance(qr_token: string, lat?: number, lng?: number) {
    return (await api.post('/attendance/mark', { qr_token, lat, lng })).data;
  },
  async getSessionRecords(sessionId: string): Promise<LiveAttendanceRecord[]> {
    return (await api.get<LiveAttendanceRecord[]>(`/attendance/sessions/${sessionId}/records`)).data;
  },
  async editRecord(recordId: string, is_present: boolean, edit_reason: string) {
    return (await api.put(`/attendance/records/${recordId}`, { is_present, edit_reason })).data;
  },
  async getMyAttendance(): Promise<AttendanceRecord[]> {
    return (await api.get<AttendanceRecord[]>('/attendance/my-attendance')).data;
  }
};
