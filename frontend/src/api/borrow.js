import api from "./index";
import { API_ENDPOINTS } from "../config/constants.js";

// Fetch all borrow records with pagination and optional filters
export const getBorrows = async (page = 1, limit = 10, filters = {}, signal) => {
  try {
    const params = {
      page,
      limit,
      ...filters,
    };

    const response = await api.get(API_ENDPOINTS.BORROW.LIST, {
      params,
      signal,
    });
    return response.data;
  } catch (error) {
    if (error.name !== "AbortError") {
      console.error("Error fetching borrow records:", error);
    }
    throw error;
  }
};

// Create a borrow record
export const borrowBook = async (borrowData, signal) => {
  try {
    const response = await api.post(API_ENDPOINTS.BORROW.CREATE, borrowData, {
      signal,
    });
    return response.data;
  } catch (error) {
    if (error.name !== "AbortError") {
      console.error("Error creating borrow record:", error);
    }
    throw error;
  }
};

// Return a borrowed book
export const returnBook = async (borrowId, signal) => {
  try {
    const response = await api.patch(
      API_ENDPOINTS.BORROW.RETURN(borrowId),
      {},
      { signal }
    );
    return response.data;
  } catch (error) {
    if (error.name !== "AbortError") {
      console.error("Error returning book:", error);
    }
    throw error;
  }
};
