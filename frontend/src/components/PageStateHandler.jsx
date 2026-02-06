import { Box, CircularProgress, Alert } from "@mui/material";

/**
 * Reusable component to handle loading, empty, and error states
 * @param {boolean} loading - Is data being loaded
 * @param {array} data - Data array
 * @param {string} emptyMessage - Message to show when data is empty
 * @param {ReactNode} children - Content to show when data is loaded
 */
const PageStateHandler = ({
  loading,
  data,
  emptyMessage = "No data available at the moment.",
  children,
}) {
  // Loading State
  if (loading) {
    return (
      <Box sx={{ display: "flex", justifyContent: "center", py: 5 }}>
        <CircularProgress />
      </Box>
    );
  }

  // Empty State
  if (!loading && data.length === 0) {
    return (
      <Alert severity="info" sx={{ mt: 2 }}>
        {emptyMessage}
      </Alert>
    );
  }

  // Data State
  return children;
};

export default PageStateHandler;
