/**
 * API Response Handler Utilities
 * Handles normalization and formatting of API responses
 */

/**
 * Extract response data from API response
 * Handles both paginated and non-paginated responses
 * 
 * @param {Object} response - API response object
 * @returns {Object} - Normalized response with data and pagination
 * 
 * Example:
 * Input: { data: [...], pagination: { total, page, limit, pages } }
 * Output: { data: [...], pagination: { total, page, limit, pages } }
 * 
 * Input: { id: 1, name: "Item" }
 * Output: { data: { id: 1, name: "Item" }, pagination: null }
 */
export const extractResponseData = (response) => {
  if (!response) {
    return { data: [], pagination: null };
  }

  // Check if response has paginated format
  if (response.data && response.pagination) {
    return {
      data: response.data,
      pagination: response.pagination,
    };
  }

  // Check if response is an array (non-paginated list)
  if (Array.isArray(response)) {
    return {
      data: response,
      pagination: null,
    };
  }

  // Single object response
  return {
    data: response,
    pagination: null,
  };
};
