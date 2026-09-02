import axios from "axios";
import { isTokenExpired } from "../utils/jwt";

const baseURL =
  import.meta.env.VITE_API_BASE_URL ||
  import.meta.env.VITE_API_URL ||
  (import.meta.env.DEV ? "http://localhost:8000/api" : "/api");

const api = axios.create({
  baseURL,
  Headers: { "Content-Type": "application/json" },
});

function clearAuthState() {
  localStorage.removeItem("token");
  localStorage.removeItem("user");
}

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("token");

    if (token) {
      if (isTokenExpired(token)) {
        clearAuthState();

        if (typeof window !== "undefined") {
          window.location.replace("/");
        }

        return Promise.reject(new Error("Token expired"));
      }

      config.headers = config.headers ?? {};
      config.headers.Authorization = `Bearer ${token}`;
    }

    return config;
  },
  (error) => Promise.reject(error),
);

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      clearAuthState();

      if (typeof window !== "undefined") {
        window.location.replace("/");
      }
    }

    return Promise.reject(error);
  },
);

export default api;
