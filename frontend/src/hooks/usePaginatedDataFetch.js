import { useState, useEffect, useCallback, useRef } from "react";
import { extractResponseData } from "../utils/apiResponseHandler";
import { PAGINATION } from "../config/constants";

/**
 * Helper to check if error is due to request cancellation
 */
const isCancellationError = (err) => {
  return (
    err.name === "AbortError" || 
    err.message === "canceled" ||
    err.code === "ECONNABORTED"
  );
};

/**
 * Custom hook for handling paginated data fetching
 * @param {Function} fetchFunction - API function to call for fetching data (receives page, limit, signal)
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
  const controllerRef = useRef(null);

  // Fetch data from API with AbortController support
  const performFetch = useCallback(
    async (currentPage, currentPageSize, signal) => {
      try {
        const response = await fetchFunction(currentPage, currentPageSize, signal);
        const { data, pagination } = extractResponseData(response);

        // Extract the actual items array and total count
        const items = Array.isArray(data) ? data : [data];
        const total = pagination?.total || 0;

        setData(items);
        setTotalRecords(total);
      } catch (err) {
        // Ignore errors from aborted/cancelled requests
        if (isCancellationError(err)) {
          return;
        }
        console.error("Error fetching paginated data:", err);
        // Extract error message from Axios error response or fallback to error message
        const errorMessage = err.response?.data?.detail || err.message || "Failed to fetch data";
        setError(errorMessage);
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
    // Cancel previous request if it exists
    if (controllerRef.current) {
      controllerRef.current.abort();
    }

    // Create new AbortController for this fetch
    const controller = new AbortController();
    controllerRef.current = controller;

    setLoading(true);
    setError(null);
    performFetch(page, pageSize, controller.signal);

    // Cleanup: abort request if component unmounts or dependencies change
    return () => {
      controller.abort();
    };
  }, [page, pageSize, performFetch]);

  // Handle pagination change from DataTable
  const onPaginationChange = useCallback((newPage, newPageSize) => {
    setPage(newPage);
    setPageSize(newPageSize);
  }, []);

  // Refetch data with current pagination
  const refetch = useCallback(() => {
    if (controllerRef.current) {
      controllerRef.current.abort();
    }

    const controller = new AbortController();
    controllerRef.current = controller;

    setLoading(true);
    setError(null);
    return performFetch(page, pageSize, controller.signal);
  }, [page, pageSize, performFetch]);

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
 * @param {Function} fetchFunction - API function to call for fetching data (receives page, limit, filters, signal)
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
    (currentPage, currentPageSize, signal) => {
      return fetchFunction(currentPage, currentPageSize, filters, signal);
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
