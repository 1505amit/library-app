import { useState, useEffect } from "react";
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
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Grid,
} from "@mui/material";
import DataTable from "../components/DataTable";
import PageStateHandler from "../components/PageStateHandler";
import Notification from "../components/Notification";
import BorrowFormModal from "../components/BorrowFormModal";
import { useDataFetch } from "../hooks/useDataFetch";
import { getBorrows, borrowBook, returnBook } from "../api/borrow";
import { getBooks } from "../api/books";
import { getMembers } from "../api/members";
import { formatDateTime } from "../utils/dateFormatter";

const BorrowPage = () => {
  const [includeReturned, setIncludeReturned] = useState(true);
  const [selectedMemberId, setSelectedMemberId] = useState("");
  const [selectedBookId, setSelectedBookId] = useState("");
  
  // Data for filter dropdowns
  const [books, setBooks] = useState([]);
  const [members, setMembers] = useState([]);
  const [loadingFilters, setLoadingFilters] = useState(true);

  const { data: borrows, loading, error: fetchError, openSnackbar: openFetchNotification, setOpenSnackbar: setOpenFetchNotification, refetch } =
    useDataFetch(() => getBorrows(includeReturned, selectedMemberId || null, selectedBookId || null), [includeReturned, selectedMemberId, selectedBookId]);

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

  // Fetch books and members for filter dropdowns
  useEffect(() => {
    const fetchFilterData = async () => {
      try {
        setLoadingFilters(true);
        const [booksData, membersData] = await Promise.all([
          getBooks(),
          getMembers()
        ]);
        setBooks(booksData);
        setMembers(membersData);
      } catch (error) {
        console.error("Error fetching filter data:", error);
      } finally {
        setLoadingFilters(false);
      }
    };

    fetchFilterData();
  }, []);

  // Handle filter changes
  const handleMemberFilterChange = (event) => {
    setSelectedMemberId(event.target.value);
  };

  const handleBookFilterChange = (event) => {
    setSelectedBookId(event.target.value);
  };

  const clearFilters = () => {
    setSelectedMemberId("");
    setSelectedBookId("");
  };

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
      <Box sx={{ mt: 4, pb: 10 }}>
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
        <Box sx={{ mb: 3, p: 2, border: 1, borderColor: 'grey.300', borderRadius: 1 }}>
          <Typography variant="h6" sx={{ mb: 2 }}>Filters</Typography>
          
          <Grid container spacing={2} alignItems="center">
            {/* Include Returned Checkbox */}
            <Grid item xs={12} sm={6} md={3}>
              <FormControlLabel
                control={
                  <Checkbox
                    checked={includeReturned}
                    onChange={(e) => setIncludeReturned(e.target.checked)}
                  />
                }
                label="Returned Books"
              />
            </Grid>

            {/* Member Filter */}
            <Grid item xs={12} sm={6} md={3}>
              <FormControl fullWidth size="small">
                <InputLabel id="member-filter-label">Filter by Member</InputLabel>
                <Select
                  labelId="member-filter-label"
                  value={selectedMemberId}
                  label="Filter by Member"
                  onChange={handleMemberFilterChange}
                  disabled={loadingFilters}
                >
                  <MenuItem value="">All Members</MenuItem>
                  {members.map((member) => (
                    <MenuItem key={member.id} value={member.id}>
                      {member.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>

            {/* Book Filter */}
            <Grid item xs={12} sm={6} md={3}>
              <FormControl fullWidth size="small">
                <InputLabel id="book-filter-label">Filter by Book</InputLabel>
                <Select
                  labelId="book-filter-label"
                  value={selectedBookId}
                  label="Filter by Book"
                  onChange={handleBookFilterChange}
                  disabled={loadingFilters}
                >
                  <MenuItem value="">All Books</MenuItem>
                  {books.map((book) => (
                    <MenuItem key={book.id} value={book.id}>
                      {book.title}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>

            {/* Clear Filters Button */}
            <Grid item xs={12} sm={6} md={3}>
              <Button
                variant="outlined"
                onClick={clearFilters}
                disabled={!selectedMemberId && !selectedBookId}
                size="small"
              >
                Clear Filters
              </Button>
            </Grid>
          </Grid>
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
