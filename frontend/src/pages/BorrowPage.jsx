import { useState } from "react";
import {
  Container,
  Typography,
  Box,
  FormControlLabel,
  Checkbox,
  Button,
} from "@mui/material";
import DataTable from "../components/DataTable";
import PageStateHandler from "../components/PageStateHandler";
import Notification from "../components/Notification";
import BorrowFormModal from "../components/BorrowFormModal";
import { useDataFetch } from "../hooks/useDataFetch";
import { getBorrows, borrowBook } from "../api/borrow";
import { formatDateTime } from "../utils/dateFormatter";

const BorrowPage = () => {
  const [includeReturned, setIncludeReturned] = useState(true);
  const { data: borrows, loading, error: fetchError, openSnackbar: openFetchNotification, setOpenSnackbar: setOpenFetchNotification, refetch } =
    useDataFetch(() => getBorrows(includeReturned), [includeReturned]);

  // Modal and borrow states
  const [openBorrowModal, setOpenBorrowModal] = useState(false);
  const [borrowLoading, setBorrowLoading] = useState(false);
  const [successMessage, setSuccessMessage] = useState("");
  const [openSuccessSnackbar, setOpenSuccessSnackbar] = useState(false);
  const [borrowError, setBorrowError] = useState("");
  const [openErrorSnackbar, setOpenErrorSnackbar] = useState(false);

  // Handle borrow submission from modal
  const handleBorrow = async (borrowData) => {
    try {
      setBorrowLoading(true);
      await borrowBook(borrowData);

      // Success
      setSuccessMessage("Book borrowed successfully!");
      setOpenSuccessSnackbar(true);
      setOpenBorrowModal(false);

      // Reload borrow records
      await refetch();
    } catch (error) {
      const errorMsg =
        error.response?.data?.detail || "Failed to borrow book. Please try again.";
      setBorrowError(errorMsg);
      setOpenErrorSnackbar(true);
      console.error("Error borrowing book:", error);
    } finally {
      setBorrowLoading(false);
    }
  };

  const columns = [
    { field: "id", headerName: "ID" },
    { field: "book.title", headerName: "Book" },
    { field: "member.name", headerName: "Member" },
    {
      field: "borrowed_at",
      headerName: "Borrowed On",
      render: (value) => formatDateTime(value),
    },
    {
      field: "returned_at",
      headerName: "Returned On",
      render: (value) => (value ? formatDateTime(value) : "-"),
    },
  ];

  const handleReturn = (borrow) => {
    console.log(`Returning book: ${borrow.book_title}`);
    // TODO: integrate with return API
  };

  return (
    <Container maxWidth="lg">
      <Box sx={{ mt: 4 }}>
        {/* Heading with Borrow Button */}
        <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", mb: 3 }}>
          <Typography variant="h4">
            Borrowed Books
          </Typography>
          <Button
            variant="contained"
            onClick={() => setOpenBorrowModal(true)}
          >
            Borrow a Book
          </Button>
        </Box>

        {/* Filter Section */}
        <Box sx={{ mb: 3 }}>
          <FormControlLabel
            control={
              <Checkbox
                checked={includeReturned}
                onChange={(e) => setIncludeReturned(e.target.checked)}
              />
            }
            label="Include Returned Books"
          />
        </Box>

        <PageStateHandler
          loading={loading}
          data={borrows}
          emptyMessage="No borrow records available at the moment."
        >
          <DataTable
            columns={columns}
            rows={borrows}
            onAction={{
              label: "Return",
              handler: handleReturn,
              disabled: (row) => !!row.returned_at,
            }}
          />
        </PageStateHandler>

        {/* Borrow Form Modal */}
        <BorrowFormModal
          open={openBorrowModal}
          onClose={() => setOpenBorrowModal(false)}
          onSubmit={handleBorrow}
          isLoading={borrowLoading}
        />

        {/* Error Notification */}
        <Notification
          open={openErrorSnackbar}
          message={borrowError}
          type="error"
          onClose={() => setOpenErrorSnackbar(false)}
        />

        {/* Success Notification */}
        <Notification
          open={openSuccessSnackbar}
          message={successMessage}
          type="success"
          onClose={() => setOpenSuccessSnackbar(false)}
        />

        {/* Fetch Error Notification */}
        <Notification
          open={openFetchNotification}
          message={fetchError}
          type="error"
          onClose={() => setOpenFetchNotification(false)}
        />
      </Box>
    </Container>
  );
};

export default BorrowPage;
