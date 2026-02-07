import { Snackbar, Alert } from "@mui/material";

/**
 * Reusable Snackbar component for displaying messages with different types
 * @param {boolean} open - Whether the snackbar is open
 * @param {string} message - The message to display
 * @param {string} type - Type of message: 'success', 'error', 'warning', 'info'
 * @param {function} onClose - Callback when snackbar closes
 * @param {number} autoHideDuration - Duration in milliseconds before auto-closing (0 = no auto-close)
 */
const Notification = ({
  open,
  message,
  type = "info",
  onClose,
  autoHideDuration = 6000,
}) => {
  // Map message types to Alert severity
  const severityMap = {
    success: "success",
    error: "error",
    warning: "warning",
    info: "info",
  };

  const severity = severityMap[type] || "info";

  return (
    <Snackbar
      open={open}
      autoHideDuration={autoHideDuration}
      onClose={onClose}
      anchorOrigin={{ vertical: "bottom", horizontal: "left" }}
    >
      <Alert 
        onClose={onClose} 
        severity={severity}
        variant="filled"
        sx={{ 
          width: "100%",
          fontSize: "0.95rem",
          fontWeight: 500,
        }}
      >
        {message}
      </Alert>
    </Snackbar>
  );
};

export default Notification;
