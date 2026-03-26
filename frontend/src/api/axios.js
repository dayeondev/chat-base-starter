import axios from 'axios';
import { env } from '../config';

const api = axios.create({
  baseURL: env.VITE_API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    // Add Request ID for tracing
    config.headers['X-Request-ID'] = crypto.randomUUID();
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle errors
api.interceptors.response.use(
  (response) => {
    const requestId = response.config.headers['X-Request-ID'];
    if (requestId) {
      console.log(`[${requestId}] ✅ ${response.config.method?.toUpperCase()} ${response.config.url}`);
    }
    return response;
  },
  (error) => {
    const requestId = error.config?.headers['X-Request-ID'];
    if (requestId) {
      console.error(`[${requestId}] ❌ ${error.config?.method?.toUpperCase()} ${error.config?.url} - ${error.response?.status}`);
      console.error(`[${requestId}] Trace ID: ${requestId} - Search in Grafana Loki: {container_name=~"chat-base-starter-.*"} |= "${requestId}"`);
    }
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;
