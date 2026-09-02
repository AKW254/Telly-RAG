import axios from "axios";
import api from "../api/axios";
import { isTokenExpired } from "../utils/jwt";

function extractErrorMessage(error, fallbackMessage) {
  if (!axios.isAxiosError(error)) {
    if (error instanceof Error && error.message) {
      return error.message;
    }

    return fallbackMessage;
  }

  const data = error.response?.data;

  if (typeof data === "string" && data.trim()) {
    return data;
  }

  if (data && typeof data === "object") {
    if (typeof data.message === "string" && data.message.trim()) {
      return data.message;
    }

    if (typeof data.detail === "string" && data.detail.trim()) {
      return data.detail;
    }

    if (Array.isArray(data.detail)) {
      const detailMessage = data.detail
        .map((item) => {
          if (typeof item === "string") {
            return item;
          }

          if (item && typeof item === "object") {
            return item.msg || item.message || item.detail || "";
          }

          return "";
        })
        .filter(Boolean)
        .join(", ");

      if (detailMessage) {
        return detailMessage;
      }
    }
  }

  return fallbackMessage;
}

function throwAuthError(error, fallbackMessage) {
  throw new Error(extractErrorMessage(error, fallbackMessage));
}

// =============================
// Register User
// =============================
export const registerUser = async (userData) => {
  try {
    const response = await api.post("/auth/register", userData);

    return response.data;
  } catch (error) {
    throwAuthError(error, "Registration failed");
  }
};

// =============================
// Login User
// =============================
export const loginUser = async (credentials) => {
  try {
    const response = await api.post("/auth/login", credentials);

    // Save token
    if (response.data.access_token) {
      localStorage.setItem("token", response.data.access_token);
    }

    // Save user info (optional)
    if (response.data.user) {
      localStorage.setItem("user", JSON.stringify(response.data.user));
    }

    return response.data;
  } catch (error) {
    throwAuthError(error, "Login failed");
  }
};

// =============================
// Logout User
// =============================
export const logoutUser = () => {
  localStorage.removeItem("token");
  localStorage.removeItem("user");
};

// =============================
// Get Current Token
// =============================
export const getToken = () => {
  const token = localStorage.getItem("token");

  if (!token) {
    return null;
  }

  if (isTokenExpired(token)) {
    logoutUser();
    return null;
  }

  return token;
};

// =============================
// Get Current User
// =============================
export const getCurrentUser = () => {
  const user = localStorage.getItem("user");

  if (!user) {
    return null;
  }

  try {
    return JSON.parse(user);
  } catch {
    localStorage.removeItem("user");

    return null;
  }
};

// =============================
// Check Authentication
// =============================
export const isAuthenticated = () => {
  return !!getToken();
};

// =============================
// Auth Header Helper
// =============================
export const authHeader = () => {
  const token = getToken();

  if (!token) {
    return {};
  }

  return {
    Authorization: `Bearer ${token}`,
  };
};
