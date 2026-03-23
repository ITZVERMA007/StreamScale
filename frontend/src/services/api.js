import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

const api = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  timeout: 30000,
});

api.interceptors.request.use(
  (config) => {
    if (!config.data instanceof FormData){
    config.headers["Content-Type"] = "application/json";
    }
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
      console.error("Network Error:", error.response?.data?.detail);
    }
    return Promise.reject(error);
  }
);

export const uploadVideo = async (file, onProgress) => {

  const initResponse = await api.post('/upload',{
    filename: file.name
  })
  const {task_id,upload_url} = initResponse.data;

  await axios.put(upload_url,file,{
    headers:{
      'Content-Type':file.type || 'application/octet-stream',
    },
    onUploadProgress:(progressEvent) => {
      if (progressEvent.total && onProgress){
        const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
        onProgress(progress);
      }
    },
  })

  await api.post(`/process/${task_id}`);
  
  return {task_id};
};

export const getTaskStatus = async (taskId) => {
  const response = await api.get(`/tasks/${taskId}/status`);
  return response.data;
};

export const cancelTask = async (taskId) => {
  await api.post(`/tasks/${taskId}/cancel`);
};

export const getDownloadUrl = async (taskId,resolution) => {
  const response = await api.get(`/download/${taskId}/${resolution}`);
  return response.data;
};
export default api;
