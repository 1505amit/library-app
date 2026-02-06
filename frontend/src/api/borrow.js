import api from "./index";

// Fetch all borrow records with optional filter
export const getBorrows = async (includeReturned = true) => {
  try {
    const response = await api.get("/borrow/", {
      params: {
        include_returned: includeReturned,
      },
    });
    return response.data;
  } catch (error) {
    console.error("Error fetching borrow records:", error);
    throw error;
  }
};
