import { useState, useEffect } from "react";

/**
 * Custom hook to fetch data with loading, error, and snackbar management
 * @param {Function} fetchFunction - Async function that fetches data
 * @param {Array} dependencies - Dependency array for useEffect
 * @returns {Object} { data, loading, error, openSnackbar, setOpenSnackbar }
 */
export const useDataFetch = (fetchFunction, dependencies = []) => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [openSnackbar, setOpenSnackbar] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        const result = await fetchFunction();
        setData(result);
      } catch (err) {
        const errorMessage =
          err.response?.data?.detail || "Failed to load data. Please try again.";
        setError(errorMessage);
        setOpenSnackbar(true);
        console.error("Data fetch error:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, dependencies);

  return { data, loading, error, openSnackbar, setOpenSnackbar };
};
