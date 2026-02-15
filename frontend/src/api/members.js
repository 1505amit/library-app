import api from "./index";
import { API_ENDPOINTS } from "../config/constants.js";

// Fetch all members with pagination support
export const getMembers = async (page = 1, limit = 10) => {
  try {
    const response = await api.get(API_ENDPOINTS.MEMBERS.LIST, {
      params: {
        page,
        limit,
      },
    });
    return response.data;
  } catch (error) {
    console.error("Error fetching members:", error);
    throw error;
  }
};

// Create a new member
export const createMember = async (memberData) => {
  try {
    const response = await api.post(API_ENDPOINTS.MEMBERS.CREATE, memberData);
    return response.data;
  } catch (error) {
    console.error("Error creating member:", error);
    throw error;
  }
};

// Update an existing member
export const updateMember = async (memberId, memberData) => {
  try {
    const response = await api.put(
      API_ENDPOINTS.MEMBERS.UPDATE(memberId),
      memberData
    );
    return response.data;
  } catch (error) {
    console.error("Error updating member:", error);
    throw error;
  }
};
