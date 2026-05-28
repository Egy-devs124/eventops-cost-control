import axios from "axios";

export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api";

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: { "Content-Type": "application/json" },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("eventops.access");
  const language = localStorage.getItem("eventops.language") || "en";
  config.headers["Accept-Language"] = language;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("eventops.access");
      localStorage.removeItem("eventops.refresh");
    }
    return Promise.reject(error);
  }
);

export function listFromResponse(data) {
  if (Array.isArray(data)) return data;
  return data?.results || [];
}

export function countFromResponse(data) {
  if (Array.isArray(data)) return data.length;
  return data?.count || 0;
}
