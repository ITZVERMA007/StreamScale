import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  timeout: 30000,
});

api.interceptors.request.use(
  (config) => {
    config.headers["Content-Type"] = "application/json";
    return config;
  },
  (error) => Promise.reject(error)
);

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      console.error("API Error:", {
        status: error.response.status,
        data: error.response.data,
      });
    } else {
      console.error("Network Error:", error.message);
    }
    return Promise.reject(error);
  }
);

export const uploadVideo = async (file, onProgress) => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await api.post('/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    onUploadProgress: (progressEvent) => {
      if (progressEvent.total && onProgress) {
        const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
        onProgress(progress);
      }
    },
  });

  return response.data;
};

export const getTaskStatus = async (taskId) => {
  const response = await api.get(`/tasks/${taskId}/status`);
  return response.data;
};

export const cancelTask = async (taskId) => {
  await api.post(`/tasks/${taskId}/cancel`);
};

export const getDownloadUrl = async (taskId) => {
  const response = await api.get(`/tasks/${taskId}/download`);
  return response.data;
};
export default api;
