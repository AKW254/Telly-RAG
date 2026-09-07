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


// Get list of Chats
export const getChats = async () => {
  try {
    const response = await api.get("/chats");
    return response.data;
    } catch (error) {
    throwError(error, "Failed to fetch chats");
  }
};

// Get a specific chat by ID
export const getChatById = async (id) => {
  try {
    const response = await api.get(`/chats/${id}`);
    return response.data;
  } catch (error) {
    throwError(error, `Failed to fetch chat with ID: ${id}`);
  }
};

// Create a new chat
export const createChat = async (chatData) => {
    try {
    const response = await api.post("/chats", chatData);
    return response.data;
  }catch (error) {
    throwError(error, "Failed to create chat");
  }
};

// Update an existing chat
export const updateChat = async (id, chatData) => {
  try {
    const response = await api.put(`/chats/${id}`, chatData);
    return response.data;
  } catch (error) {
    throwError(error, `Failed to update chat with ID: ${id}`);
  }
};

// Delete a chat
export const deleteChat = async (id) => {
  try {
    const response = await api.delete(`/chats/${id}`);
    return response.data;
  }catch (error) {
    throwError(error, `Failed to delete chat with ID: ${id}`);
  }
}



