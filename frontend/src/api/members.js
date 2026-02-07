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

// Create a new member
export const createMember = async (memberData) => {
  try {
    const response = await api.post("/members/", memberData);
    return response.data;
  } catch (error) {
    console.error("Error creating member:", error);
    throw error;
  }
};

// Update an existing member
export const updateMember = async (memberId, memberData) => {
  try {
    const response = await api.put(`/members/${memberId}`, memberData);
    return response.data;
  } catch (error) {
    console.error("Error updating member:", error);
    throw error;
  }
};
