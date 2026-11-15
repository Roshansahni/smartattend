import { api } from './api';
import type { Course } from '@/types';

export const DEFAULT_COURSES: Course[] = [
  {
    id: 'bc8844a8-25a0-42e8-ad27-153ed7a89676',
    code: 'CS701',
    name: 'Artificial Intelligence & Machine Learning',
    description: 'Final Year 7th Sem Core (AI & DS Specialization)',
    credit_hours: 4,
    semester: 7,
    is_active: true,
    created_at: new Date().toISOString(),
    department: {
      id: 'b770c6f2-17d2-418c-9ab4-74bb1223e279',
      name: 'Computer Science & Engineering',
      code: 'CSE'
    }
  },
  {
    id: '7da9d338-2587-46ce-8097-07903daa3bb0',
    code: 'AI702',
    name: 'Deep Learning & Neural Networks',
    description: 'Advanced Applied AI & Data Systems',
    credit_hours: 4,
    semester: 7,
    is_active: true,
    created_at: new Date().toISOString(),
    department: {
      id: 'b770c6f2-17d2-418c-9ab4-74bb1223e279',
      name: 'Computer Science & Engineering',
      code: 'CSE'
    }
  },
  {
    id: '8b29b304-7b1f-4643-af10-56e63ae1160d',
    code: 'CS401',
    name: 'Distributed Systems & Cloud Computing',
    description: 'Core final year CSE course',
    credit_hours: 4,
    semester: 7,
    is_active: true,
    created_at: new Date().toISOString(),
    department: {
      id: 'b770c6f2-17d2-418c-9ab4-74bb1223e279',
      name: 'Computer Science & Engineering',
      code: 'CSE'
    }
  }
];

export const courseService = {
  async getCourses(): Promise<Course[]> {
    try {
      const { data } = await api.get<Course[]>('/courses');
      if (Array.isArray(data) && data.length > 0) {
        return data;
      }
      return DEFAULT_COURSES;
    } catch (err) {
      return DEFAULT_COURSES;
    }
  }
};
