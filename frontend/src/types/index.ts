export type Role = 'super_admin' | 'admin' | 'faculty' | 'student';

export interface User {
  id: string;
  email: string;
  full_name: string;
  phone?: string;
  is_active: boolean;
  is_verified: boolean;
  roles: string[];
  created_at: string;
  last_login?: string;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;
}

export interface Department {
  id: string;
  name: string;
  code: string;
  description?: string;
  is_active: boolean;
  created_at: string;
}

export interface Student {
  id: string;
  enrollment_number: string;
  semester: number;
  batch_year: number;
  section?: string;
  is_active: boolean;
  created_at: string;
  user: { id: string; email: string; full_name: string; phone?: string; is_active: boolean };
  department: { id: string; name: string; code: string };
}

export interface Faculty {
  id: string;
  employee_id: string;
  designation: string;
  specialization?: string;
  is_active: boolean;
  joined_date?: string;
  created_at: string;
  user: { id: string; email: string; full_name: string; phone?: string; is_active: boolean };
  department: { id: string; name: string; code: string };
}

export interface Course {
  id: string;
  code: string;
  name: string;
  description?: string;
  credit_hours: number;
  semester: number;
  is_active: boolean;
  created_at: string;
  department: { id: string; name: string; code: string };
}

export interface AttendanceSession {
  id: string;
  course_id: string;
  faculty_id: string;
  academic_session_id: string;
  title: string;
  started_at?: string;
  ended_at?: string;
  is_active: boolean;
  gps_required: boolean;
  location_lat?: number;
  location_lng?: number;
  location_radius_meters: number;
  created_at: string;
}

export interface QRTokenData {
  session_id: string;
  qr_image_base64: string;
  token_expires_at: string;
  refresh_interval_seconds: number;
}

export interface AttendanceRecord {
  id: string;
  attendance_session_id: string;
  student_id: string;
  marked_at: string;
  is_present: boolean;
  verification_method: string;
  distance_meters?: number;
  is_edited: boolean;
  edit_reason?: string;
  created_at: string;
}

export interface LiveAttendanceRecord {
  record_id: string;
  student_id: string;
  student_name: string;
  enrollment_number: string;
  marked_at: string;
  verification_method: string;
  is_edited: boolean;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}
