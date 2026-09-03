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

//Add Document data
export const addDocument = async (formData) => {
  try {
    const response = await api.post("/documents/upload", formData);
    return response.data;
  } catch (error) {
    throwError(error, "Failed to add document");
  }
};

//Get Single Document data
export const getDocument = async (documentId) => {
  try {
    const response = await api.get(`/documents/${documentId}`);
    return response.data;
  } catch (error) {
    throwError(error, "Failed to fetch document");
  }
};

export const downloadDocument = async (documentId) => {
  try {
    const response = await api.get(`/documents/${documentId}/download`, {
      responseType: "blob",
    });
    return response.data;
  } catch (error) {
    throwError(error, "Failed to download document");
  }
};

export const updateDocument = async (documentId, formData) => {
  try {
    const response = await api.put(`/documents/${documentId}`, formData);
    return response.data;
  } catch (error) {
    throwError(error, "Failed to update document");
  }
};

export const deleteDocument = async (documentId) => {
  try {
    await api.delete(`/documents/${documentId}`);
  } catch (error) {
    throwError(error, "Failed to delete document");
  }
};
