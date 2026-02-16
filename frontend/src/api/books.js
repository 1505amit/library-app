import api from "./index";
import { API_ENDPOINTS } from "../config/constants.js";

// Fetch all books with pagination support
export const getBooks = async (page = 1, limit = 10, signal) => {
  try {
    const response = await api.get(API_ENDPOINTS.BOOKS.LIST, {
      params: {
        page,
        limit,
      },
      signal,
    });
    return response.data;
  } catch (error) {
    // Don't log abort errors
    if (error.name !== "AbortError") {
      console.error("Error fetching books:", error);
    }
    throw error;
  }
};

// Create a new book
export const createBook = async (bookData, signal) => {
  try {
    const response = await api.post(API_ENDPOINTS.BOOKS.CREATE, bookData, {
      signal,
    });
    return response.data;
  } catch (error) {
    if (error.name !== "AbortError") {
      console.error("Error creating book:", error);
    }
    throw error;
  }
};

// Update an existing book
export const updateBook = async (bookId, bookData, signal) => {
  try {
    const response = await api.put(
      API_ENDPOINTS.BOOKS.UPDATE(bookId),
      bookData,
      { signal }
    );
    return response.data;
  } catch (error) {
    if (error.name !== "AbortError") {
      console.error("Error updating book:", error);
    }
    throw error;
  }
};
