import { api } from './api';
import type { Student, PaginatedResponse } from '@/types';

export const studentService = {
  async getStudents(page = 1, page_size = 20, search = ''): Promise<PaginatedResponse<Student>> {
    const { data } = await api.get<PaginatedResponse<Student>>('/students', {
      params: { page, page_size, search }
    });
    return data;
  }
};
