import axios from 'axios';

/**
 * Centralized Axios client configured with base URL and response interceptors.
 * Designed to cleanly handle development proxies and production Vercel/Render deployments.
 */
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

// Request Interceptor: Attach authentication tokens or headers in future milestones
apiClient.interceptors.request.use(
  (config) => {
    // Milestone 5: Attach Authorization: Bearer <token>
    return config;
  },
  (error) => Promise.reject(error)
);

// Response Interceptor: Standardize API responses and error formatting
apiClient.interceptors.response.use(
  (response) => response.data,
  (error) => {
    const errorPayload = {
      message:
        error.response?.data?.error ||
        error.response?.data?.message ||
        error.response?.data?.detail ||
        error.message ||
        'An unexpected error occurred',
      status: error.response?.status,
      errors: error.response?.data?.errors || null,
    };
    return Promise.reject(errorPayload);
  }
);

export default apiClient;
