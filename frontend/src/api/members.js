import api from "./index";

// Fetch all members
export const getMembers = async () => {
  try {
    const response = await api.get("/members/");
    return response.data;
  } catch (error) {
    console.error("Error fetching members:", error);
    throw error;
  }
};
