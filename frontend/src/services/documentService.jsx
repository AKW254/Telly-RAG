import axios from "axios";
import api from "../api/axios";

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

function throwError(error, fallbackMessage) {
  throw new Error(extractErrorMessage(error, fallbackMessage));
}

//Get Document data
export const getDocuments = async () => {
    try {
    const response = await api.get("/documents");
    return response.data;
    } catch (error) {
    throwError(error, "Failed to fetch documents");
    }
};