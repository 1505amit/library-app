import api from "./index";
import { API_ENDPOINTS } from "../config/constants.js";

// Fetch all borrow records with pagination and optional filters
export const getBorrows = async (page = 1, limit = 10, filters = {}) => {
  try {
    const params = {
      page,
      limit,
      ...filters,
    };

    const response = await api.get(API_ENDPOINTS.BORROW.LIST, {
      params,
    });
    return response.data;
  } catch (error) {
    console.error("Error fetching borrow records:", error);
    throw error;
  }
};

// Create a borrow record
export const borrowBook = async (borrowData) => {
  try {
    const response = await api.post(API_ENDPOINTS.BORROW.CREATE, borrowData);
    return response.data;
  } catch (error) {
    console.error("Error creating borrow record:", error);
    throw error;
  }
};

// Return a borrowed book
export const returnBook = async (borrowId) => {
  try {
    const response = await api.patch(
      API_ENDPOINTS.BORROW.RETURN(borrowId)
    );
    return response.data;
  } catch (error) {
    console.error("Error returning book:", error);
    throw error;
  }
};
