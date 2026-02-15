import React from "react";
import { Box, Container, Typography, Button, Alert } from "@mui/material";
import { ROUTE_PATHS } from "../config/routes";

/**
 * Fallback UI Component for ErrorBoundary
 */
const ErrorFallback = ({ error, onReset }) => {
  const handleGoHome = () => {
    onReset();
    window.location.href = ROUTE_PATHS.HOME;
  };

  return (
    <Container maxWidth="sm">
      <Box
        sx={{
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          alignItems: "center",
          minHeight: "100vh",
        }}
      >
        <Box
          sx={{
            textAlign: "center",
          }}
        >
          <Typography variant="h4" component="h1" gutterBottom sx={{ fontWeight: "bold" }}>
            Oops! Something went wrong
          </Typography>
          <Typography variant="body1" color="textSecondary" sx={{ marginBottom: 3 }}>
            We're sorry for the inconvenience. An unexpected error occurred.
          </Typography>

          <Button
            variant="contained"
            color="primary"
            size="large"
            onClick={handleGoHome}
            sx={{ paddingX: 4, paddingY: 1.5 }}
          >
            Go to Home
          </Button>
        </Box>
      </Box>
    </Container>
  );
};

/**
 * ErrorBoundary Component
 * Catches JavaScript errors anywhere in the child component tree and displays a fallback UI
 */
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
    };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    console.error("Error caught by ErrorBoundary:", error, errorInfo);

    this.setState({
      error: error,
    });
  }

  handleReset = () => {
    this.setState({
      hasError: false,
      error: null,
    });
  };

  render() {
    if (this.state.hasError) {
      return <ErrorFallback error={this.state.error} onReset={this.handleReset} />;
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
