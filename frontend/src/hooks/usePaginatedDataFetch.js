import { useState, useEffect, useCallback } from "react";
import { extractResponseData } from "../utils/apiResponseHandler";
import { PAGINATION } from "../config/constants";

/**
 * Custom hook for handling paginated data fetching
 * @param {Function} fetchFunction - API function to call for fetching data
 * @param {number} initialPage - Starting page (default: 1)
 * @param {number} initialLimit - Items per page (default: PAGINATION.DEFAULT_LIMIT)
 * @returns {Object} - Data, pagination info, loading state, error, and handlers
 */
export const usePaginatedDataFetch = (
  fetchFunction,
  initialPage = 1,
  initialLimit = PAGINATION.DEFAULT_LIMIT
) => {
  const [data, setData] = useState([]);
  const [page, setPage] = useState(initialPage);
  const [pageSize, setPageSize] = useState(initialLimit);
  const [totalRecords, setTotalRecords] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch data from API
  const fetchData = useCallback(
    async (currentPage = page, currentPageSize = pageSize) => {
      setLoading(true);
      setError(null);
      try {
        const response = await fetchFunction(currentPage, currentPageSize);
        const { data, pagination } = extractResponseData(response);

        // Extract the actual items array and total count
        const items = Array.isArray(data) ? data : [data];
        const total = pagination?.total || 0;

        setData(items);
        setTotalRecords(total);
      } catch (err) {
        console.error("Error fetching paginated data:", err);
        setError(err.message || "Failed to fetch data");
        setData([]);
        setTotalRecords(0);
      } finally {
        setLoading(false);
      }
    },
    [fetchFunction]
  );

  // Initial data fetch and refetch on pagination changes
  useEffect(() => {
    fetchData(page, pageSize);
  }, [page, pageSize, fetchData]);

  // Handle pagination change from DataTable
  const onPaginationChange = useCallback((newPage, newPageSize) => {
    setPage(newPage);
    setPageSize(newPageSize);
  }, []);

  // Refetch data with current pagination
  const refetch = useCallback(() => {
    return fetchData(page, pageSize);
  }, [fetchData, page, pageSize]);

  // Reset pagination to initial state
  const resetPagination = useCallback(() => {
    setPage(initialPage);
    setPageSize(initialLimit);
  }, [initialPage, initialLimit]);

  return {
    data,
    totalRecords,
    page,
    pageSize,
    loading,
    error,
    onPaginationChange,
    refetch,
    resetPagination,
  };
};

/**
 * Custom hook for handling paginated data fetching with filters
 * @param {Function} fetchFunction - API function to call for fetching data (receives page, limit, filters)
 * @param {number} initialPage - Starting page (default: 1)
 * @param {number} initialLimit - Items per page (default: PAGINATION.DEFAULT_LIMIT)
 * @returns {Object} - Data, pagination info, loading state, error, handlers, and filter functions
 */
export const usePaginatedDataFetchWithFilters = (
  fetchFunction,
  initialPage = 1,
  initialLimit = PAGINATION.DEFAULT_LIMIT
) => {
  const [filters, setFilters] = useState({});

  // Create a wrapper function that includes filters
  const fetchFunctionWithFilters = useCallback(
    (currentPage, currentPageSize) => {
      return fetchFunction(currentPage, currentPageSize, filters);
    },
    [fetchFunction, filters]
  );

  // Use the base hook with the wrapped function
  const baseHook = usePaginatedDataFetch(
    fetchFunctionWithFilters,
    initialPage,
    initialLimit
  );

  // Update filters
  const updateFilters = useCallback((newFilters) => {
    setFilters(newFilters);
  }, []);

  // Apply filters and reset to first page
  const applyFilters = useCallback((newFilters) => {
    setFilters(newFilters);
    baseHook.resetPagination();
  }, [baseHook]);

  return {
    ...baseHook,
    filters,
    setFilters: updateFilters,
    applyFilters,
  };
};
