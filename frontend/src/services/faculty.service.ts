import { api } from './api';
import type { Faculty, PaginatedResponse } from '@/types';

export const facultyService = {
  async getFaculty(page = 1, page_size = 20): Promise<PaginatedResponse<Faculty>> {
    const { data } = await api.get<PaginatedResponse<Faculty>>('/faculty', {
      params: { page, page_size }
    });
    return data;
  }
};
