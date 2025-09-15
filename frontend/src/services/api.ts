import axios from 'axios';
import { 
  Schedule, 
  OptimizationResult, 
  User, 
  DemoDataRequest 
} from '../types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8040';

console.log('API Base URL:', API_BASE_URL);

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  console.log('API Request:', config.method?.toUpperCase(), config.url);
  return config;
});

// Handle auth errors
api.interceptors.response.use(
  (response) => {
    console.log('API Response:', response.config.url, response.status);
    return response;
  },
  (error) => {
    console.error('API Error:', error.config?.url, error.response?.status, error.message);
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const authService = {
  async register(email: string, password: string, fullName: string, organization?: string) {
    const response = await api.post('/register', {
      email,
      password,
      full_name: fullName,
      organization,
    });
    return response.data;
  },

  async login(email: string, password: string) {
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);
    
    const response = await api.post('/login', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    
    if (response.data.access_token) {
      localStorage.setItem('token', response.data.access_token);
    }
    return response.data;
  },

  async getCurrentUser(): Promise<User> {
    const response = await api.get('/me');
    return response.data;
  },

  logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  },
};

export const scheduleService = {
  async optimizeSchedule(schedule: Schedule): Promise<OptimizationResult> {
    const response = await api.post('/optimize-schedule', schedule);
    return response.data;
  },

  async getDemoData(request?: DemoDataRequest): Promise<Schedule> {
    const response = await api.post('/demo-data', request || {});
    return response.data;
  },

  async getComplexDemoData(): Promise<Schedule> {
    const response = await api.get('/demo-data/complex');
    return response.data;
  },

  async uploadSchedule(file: File): Promise<Schedule> {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await api.post('/upload-schedule', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  async getMySchedules(): Promise<Schedule[]> {
    const response = await api.get('/my-schedules');
    return response.data;
  },

  async getSchedule(id: string): Promise<Schedule> {
    const response = await api.get(`/schedule/${id}`);
    return response.data;
  },

  async getOptimizationHistory() {
    const response = await api.get('/optimization-history');
    return response.data;
  },
};

export default api;