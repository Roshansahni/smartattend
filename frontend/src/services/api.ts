import axios from 'axios';

export function getBaseUrl(): string {
  if (typeof window !== 'undefined') {
    const custom = localStorage.getItem('smartattend_custom_api');
    if (custom) return custom;
    if (window.location.hostname.includes('github.io')) {
      return 'https://feeds-muslim-ids-transit.trycloudflare.com/api/v1';
    }
  }
  if (import.meta.env.VITE_API_BASE_URL && !import.meta.env.VITE_API_BASE_URL.startsWith('/')) {
    return import.meta.env.VITE_API_BASE_URL;
  }
  return '/api/v1';
}

export const api = axios.create({
  baseURL: getBaseUrl(),
  headers: { 'Content-Type': 'application/json' },
});

api.interceptors.request.use((config) => {
  config.baseURL = getBaseUrl();
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config;
    if (error.response?.status === 401 && !original._retry) {
      original._retry = true;
      const rf = localStorage.getItem('refresh_token');
      if (rf) {
        try {
          const { data } = await axios.post(`${getBaseUrl()}/auth/refresh`, { refresh_token: rf });
          localStorage.setItem('access_token', data.access_token);
          original.headers.Authorization = `Bearer ${data.access_token}`;
          return api(original);
        } catch {
          localStorage.clear();
          window.location.hash = '#/login';
        }
      } else {
        localStorage.clear();
        window.location.hash = '#/login';
      }
    }
    return Promise.reject(error);
  }
);
