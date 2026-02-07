import { useState } from "react";
import {
  Container,
  Typography,
  Box,
  FormControlLabel,
  Checkbox,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from "@mui/material";
import DataTable from "../components/DataTable";
import PageStateHandler from "../components/PageStateHandler";
import Notification from "../components/Notification";
import BorrowFormModal from "../components/BorrowFormModal";
import { useDataFetch } from "../hooks/useDataFetch";
import { getBorrows, borrowBook, returnBook } from "../api/borrow";
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

  // Return confirmation states
  const [confirmDialogOpen, setConfirmDialogOpen] = useState(false);
  const [selectedBorrow, setSelectedBorrow] = useState(null);
  const [returnLoading, setReturnLoading] = useState(false);

  // Handle borrow submission from modal
  const handleBorrow = async (borrowData) => {
    try {
      setBorrowLoading(true);
      await borrowBook(borrowData);

      // Success
      setSuccessMessage("Borrow record created successfully!");
      setOpenSuccessSnackbar(true);
      setOpenBorrowModal(false);

      // Reload borrow records
      await refetch();
    } catch (error) {
      const errorMsg =
        error.response?.data?.detail || "Failed to create borrow record. Please try again.";
      setBorrowError(errorMsg);
      setOpenErrorSnackbar(true);
      console.error("Error creating borrow record:", error);
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
    setSelectedBorrow(borrow);
    setConfirmDialogOpen(true);
  };

  const handleConfirmReturn = async () => {
    if (!selectedBorrow) return;

    try {
      setReturnLoading(true);
      await returnBook(selectedBorrow.id);

      // Success
      setSuccessMessage(
        `Book "${selectedBorrow.book.title}" returned successfully!`
      );
      setOpenSuccessSnackbar(true);
      setConfirmDialogOpen(false);
      setSelectedBorrow(null);

      // Reload borrow records
      await refetch();
    } catch (error) {
      const errorMsg =
        error.response?.data?.detail ||
        "Failed to return book. Please try again.";
      setBorrowError(errorMsg);
      setOpenErrorSnackbar(true);
      console.error("Error returning book:", error);
    } finally {
      setReturnLoading(false);
    }
  };

  const handleCancelReturn = () => {
    setConfirmDialogOpen(false);
    setSelectedBorrow(null);
  };

  const actions = [
    {
      label: "Return",
      handler: handleReturn,
      disabled: (row) => row.returned_at !== null,
      color: "primary",
    },
  ];

  return (
    <Container maxWidth="lg">
      <Box sx={{ mt: 4, pb: 6 }}>
        {/* Heading with Borrow Button */}
        <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", mb: 3 }}>
          <Typography variant="h4">
            Borrow Records
          </Typography>
          <Button
            variant="contained"
            onClick={() => setOpenBorrowModal(true)}
          >
            Create Borrow Record
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
            actions={actions}
          />
        </PageStateHandler>

        {/* Borrow Form Modal */}
        <BorrowFormModal
          open={openBorrowModal}
          onClose={() => setOpenBorrowModal(false)}
          onSubmit={handleBorrow}
          isLoading={borrowLoading}
        />

        {/* Return Confirmation Dialog */}
        <Dialog
          open={confirmDialogOpen}
          onClose={handleCancelReturn}
          maxWidth="sm"
          fullWidth
        >
          <DialogTitle>Confirm Return</DialogTitle>
          <DialogContent>
            <Typography sx={{ mt: 2 }}>
              Are you sure you want to return{" "}
              <strong>"{selectedBorrow?.book?.title}"</strong> borrowed by{" "}
              <strong>{selectedBorrow?.member?.name}</strong>?
            </Typography>
          </DialogContent>
          <DialogActions>
            <Button
              onClick={handleCancelReturn}
              disabled={returnLoading}
            >
              Cancel
            </Button>
            <Button
              onClick={handleConfirmReturn}
              variant="contained"
              color="success"
              disabled={returnLoading}
            >
              {returnLoading ? "Returning..." : "Confirm Return"}
            </Button>
          </DialogActions>
        </Dialog>

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
