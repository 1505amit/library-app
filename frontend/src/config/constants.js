/**
 * API Configuration and Constants
 * Centralized configuration for the entire frontend application
 */

// API Base Configuration
// Uses environment variables via Vite for different environments
export const API_CONFIG = {
  BASE_URL: import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1",
  TIMEOUT: 30000,
  HEADERS: {
    "Content-Type": "application/json",
  },
};

// API Endpoints - Centralized endpoint definitions
export const API_ENDPOINTS = {
  BOOKS: {
    LIST: "/books",
    CREATE: "/books",
    UPDATE: (id) => `/books/${id}`,
  },
  MEMBERS: {
    LIST: "/members",
    CREATE: "/members",
    UPDATE: (id) => `/members/${id}`,
  },
  BORROW: {
    LIST: "/borrow",
    CREATE: "/borrow",
    RETURN: (id) => `/borrow/${id}/return`,
  },
};

/**
 * Pagination Configuration
 * Defines default pagination settings and metadata structure
 */
export const PAGINATION = {
  DEFAULT_PAGE: 1,
  DEFAULT_PAGE_SIZE: 10,
  PAGE_SIZE_OPTIONS: [5, 10, 25, 50],
};

/**
 * API Response Format
 * Expected structure for paginated API responses from backend
 * 
 * Example response:
 * {
 *   "data": [
 *     { "id": 1, "title": "Book 1", ... },
 *     { "id": 2, "title": "Book 2", ... }
 *   ],
 *   "pagination": {
 *     "total": 100,
 *     "page": 1,
 *     "limit": 10,
 *     "pages": 10
 *   }
 * }
 */
export const PAGINATION_META = {
  data: "data",
  pagination: {
    total: "total",
    page: "page",
    limit: "limit",
    pages: "pages",
  },
};

// Error Messages - Centralized error strings for consistency
export const ERROR_MESSAGES = {
  FETCH_FAILED: "Failed to fetch data. Please try again.",
  CREATE_FAILED: "Failed to create record. Please try again.",
  UPDATE_FAILED: "Failed to update record. Please try again.",
  DELETE_FAILED: "Failed to delete record. Please try again.",
  NETWORK_ERROR: "Network error. Please check your connection.",
  UNAUTHORIZED: "Unauthorized. Please log in again.",
  NOT_FOUND: "Resource not found.",
  SERVER_ERROR: "Server error. Please try again later.",
};
