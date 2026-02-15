import api from "./index";
import { API_ENDPOINTS } from "../config/constants.js";

// Fetch all books with pagination support
export const getBooks = async (page = 1, limit = 10) => {
  try {
    const response = await api.get(API_ENDPOINTS.BOOKS.LIST, {
      params: {
        page,
        limit,
      },
    });
    return response.data;
  } catch (error) {
    console.error("Error fetching books:", error);
    throw error;
  }
};

// Create a new book
export const createBook = async (bookData) => {
  try {
    const response = await api.post(API_ENDPOINTS.BOOKS.CREATE, bookData);
    return response.data;
  } catch (error) {
    console.error("Error creating book:", error);
    throw error;
  }
};

// Update an existing book
export const updateBook = async (bookId, bookData) => {
  try {
    const response = await api.put(
      API_ENDPOINTS.BOOKS.UPDATE(bookId),
      bookData
    );
    return response.data;
  } catch (error) {
    console.error("Error updating book:", error);
    throw error;
  }
};
