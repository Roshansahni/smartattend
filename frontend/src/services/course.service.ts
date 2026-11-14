import { api } from './api';
import type { Course } from '@/types';

export const courseService = {
  async getCourses(): Promise<Course[]> {
    const { data } = await api.get<Course[]>('/courses');
    return data;
  }
};
