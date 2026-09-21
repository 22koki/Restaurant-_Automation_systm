import axios from 'axios';

const BASE_URL =
  process.env.REACT_APP_API_URL || 'http://127.0.0.1:8000/api/';

export const api = axios.create({
  baseURL: BASE_URL,
  timeout: 15000,
  headers: {'Content-Type': 'application/json'},
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('savour_staff_token');
  if (token) config.headers.Authorization = `Token ${token}`;
  return config;
});

api.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401 && !error.config?.url?.includes('auth/login')) {
      localStorage.removeItem('savour_staff_token');
      localStorage.removeItem('savour_staff_user');
      window.dispatchEvent(new Event('savour-auth-changed'));
    }
    return Promise.reject(error);
  }
);
