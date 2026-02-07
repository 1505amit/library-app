import api from "./index";

// Fetch all books
export const getBooks = async () => {
  try {
    const response = await api.get("/books/");
    return response.data;
  } catch (error) {
    console.error("Error fetching books:", error);
    throw error;
  }
};

// Create a new book
export const createBook = async (bookData) => {
  try {
    const response = await api.post("/books/", bookData);
    return response.data;
  } catch (error) {
    console.error("Error creating book:", error);
    throw error;
  }
};

// Update an existing book
export const updateBook = async (bookId, bookData) => {
  try {
    const response = await api.put(`/books/${bookId}`, bookData);
    return response.data;
  } catch (error) {
    console.error("Error updating book:", error);
    throw error;
  }
};
