import api from "./index";

// Fetch all borrow records with optional filters
export const getBorrows = async (includeReturned = true, memberId = null, bookId = null) => {
  try {
    const params = {
      returned: includeReturned,
    };
    
    if (memberId) {
      params.member_id = memberId;
    }
    
    if (bookId) {
      params.book_id = bookId;
    }
    
    const response = await api.get("/borrow", {
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
    const response = await api.post("/borrow", borrowData);
    return response.data;
  } catch (error) {
    console.error("Error creating borrow record:", error);
    throw error;
  }
};

// Return a borrowed book
export const returnBook = async (borrowId) => {
  try {
    const response = await api.patch(`/borrow/${borrowId}/return`);
    return response.data;
  } catch (error) {
    console.error("Error returning book:", error);
    throw error;
  }
};
