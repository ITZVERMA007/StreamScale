import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

const api = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  timeout: 30000,
});

api.interceptors.request.use(
  (config) => {
    // Axios automatically sets 'application/json' for JS objects.
    // If we specifically need to avoid overriding FormData or File:
    if (config.data && !(config.data instanceof FormData) && !(typeof File !== 'undefined' && config.data instanceof File)) {
      if (!config.headers["Content-Type"]) {
        config.headers["Content-Type"] = "application/json";
      }
    }
    return config;
  },
  (error) => Promise.reject(error)
);

api.interceptors.response.use(
  (response) => response,
  (error) => {
    let errorMessage = 'An unexpected error occurred.';
    if (error.response) {
      // Server responded with error status
      const { status, data } = error.response;
      errorMessage = data?.detail || data?.message || `Server error: ${status}`;

      // Handling specific status codes
      if (status === 429) {
        errorMessage = 'Rate limit exceeded. Please wait a moment.';
      } else if (status === 413) {
        errorMessage = 'File too large. Maximum size is 2MB.';
      } else if (status === 500) {
        errorMessage = 'Server error. Please try again later.';
      }
    } else if (error.request) {
      // Request made but no response
      errorMessage = 'Network error. Please check your connection.';
    }

    console.error("API Error:", error);

    error.userMessage = errorMessage;
    return Promise.reject(error);
  }
);

export const uploadVideo = async (file, onProgress) => {

  const initResponse = await api.post('/upload', {
    filename: file.name,
    filesize: file.size
  })
  const { task_id, upload_url } = initResponse.data;

  await axios.put(upload_url, file, {
    headers: {
      'Content-Type': file.type || 'application/octet-stream',
    },
    onUploadProgress: (progressEvent) => {
      if (progressEvent.total && onProgress) {
        const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
        onProgress(progress);
      }
    },
  })

  await api.post(`/process/${task_id}`);

  return { task_id };
};

export const getTaskStatus = async (taskId) => {
  const response = await api.get(`/tasks/${taskId}/status`);
  return response.data;
};

export const cancelTask = async (taskId) => {
  await api.post(`/tasks/${taskId}/cancel`);
};

export const getDownloadUrl = async (taskId, resolution) => {
  const response = await api.get(`/download/${taskId}/${resolution}`);
  return response.data;
};
export default api;
