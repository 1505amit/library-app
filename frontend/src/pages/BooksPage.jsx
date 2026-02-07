import { useCallback, useState } from "react";
import { Container, Typography, Box, Chip, Button } from "@mui/material";
import DataTable from "../components/DataTable";
import PageStateHandler from "../components/PageStateHandler";
import Notification from "../components/Notification";
import BookFormModal from "../components/BookFormModal";
import BorrowFormModal from "../components/BorrowFormModal";
import { useDataFetch } from "../hooks/useDataFetch";
import { getBooks, createBook, updateBook } from "../api/books";
import { borrowBook } from "../api/borrow";

const BooksPage = () => {
  const { data: books, loading, error: fetchError, openSnackbar: openFetchNotification, setOpenSnackbar: setOpenFetchNotification, refetch } =
    useDataFetch(getBooks);

  const [openAddModal, setOpenAddModal] = useState(false);
  const [openEditModal, setOpenEditModal] = useState(false);
  const [openBorrowModal, setOpenBorrowModal] = useState(false);
  const [selectedBook, setSelectedBook] = useState(null);
  const [selectedBookForBorrow, setSelectedBookForBorrow] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isBorrowSubmitting, setIsBorrowSubmitting] = useState(false);
  const [notificationMessage, setNotificationMessage] = useState("");
  const [openNotification, setOpenNotification] = useState(false);
  const [notificationType, setNotificationType] = useState("info");

  const columns = [
    { field: "id", headerName: "ID" },
    { field: "title", headerName: "Title" },
    { field: "author", headerName: "Author" },
    { field: "published_year", headerName: "Year" },
    {
      field: "available",
      headerName: "Status",
      render: (value) => (
        <Chip
          label={value ? "Available" : "Not Available"}
          color={value ? "success" : "error"}
          variant={value ? "success" : "error"}
          size="small"
        />
      ),
    },
  ];

  // Open add book modal
  const handleOpenAddModal = useCallback(() => {
    setOpenAddModal(true);
  }, []);

  // Close add book modal
  const handleCloseAddModal = useCallback(() => {
    setOpenAddModal(false);
  }, []);

  // Open edit book modal
  const handleOpenEditModal = useCallback((book) => {
    setSelectedBook(book);
    setOpenEditModal(true);
  }, []);

  // Close edit book modal
  const handleCloseEditModal = useCallback(() => {
    setOpenEditModal(false);
    setSelectedBook(null);
  }, []);

  // Handle form submission for adding book
  const handleAddBook = useCallback(
    async (formData) => {
      setIsSubmitting(true);
      try {
        await createBook(formData);

        // Close modal
        handleCloseAddModal();

        // Refresh the books list
        await refetch();

        // Show success notification
        setNotificationMessage("Book added successfully!");
        setNotificationType("success");
        setOpenNotification(true);
      } catch (err) {
        console.error("Error adding book:", err);
        const errorMessage =
          err.response?.data?.detail || "Failed to add book. Please try again.";
        setNotificationMessage(errorMessage);
        setNotificationType("error");
        setOpenNotification(true);
      } finally {
        setIsSubmitting(false);
      }
    },
    [handleCloseAddModal, refetch]
  );

  // Handle form submission for updating book
  const handleUpdateBook = useCallback(
    async (formData) => {
      setIsSubmitting(true);
      try {
        await updateBook(selectedBook.id, formData);

        // Close modal
        handleCloseEditModal();

        // Refresh the books list
        await refetch();

        // Show success notification
        setNotificationMessage("Book updated successfully!");
        setNotificationType("success");
        setOpenNotification(true);
      } catch (err) {
        console.error("Error updating book:", err);
        const errorMessage =
          err.response?.data?.detail || "Failed to update book. Please try again.";
        setNotificationMessage(errorMessage);
        setNotificationType("error");
        setOpenNotification(true);
      } finally {
        setIsSubmitting(false);
      }
    },
    [selectedBook, handleCloseEditModal, refetch]
  );

  // Handle borrow action - open modal
  const handleBorrow = useCallback((book) => {
    setSelectedBookForBorrow(book);
    setOpenBorrowModal(true);
  }, []);

  // Close borrow modal
  const handleCloseBorrowModal = useCallback(() => {
    setOpenBorrowModal(false);
    setSelectedBookForBorrow(null);
  }, []);

  // Handle borrow submission
  const handleBorrowSubmit = useCallback(
    async (borrowData) => {
      setIsBorrowSubmitting(true);
      try {
        await borrowBook(borrowData);

        // Close modal
        handleCloseBorrowModal();

        // Refresh the books list
        await refetch();

        // Show success notification
        setNotificationMessage("Book borrowed successfully!");
        setNotificationType("success");
        setOpenNotification(true);
      } catch (err) {
        console.error("Error borrowing book:", err);
        const errorMessage =
          err.response?.data?.detail || "Failed to borrow book. Please try again.";
        setNotificationMessage(errorMessage);
        setNotificationType("error");
        setOpenNotification(true);
      } finally {
        setIsBorrowSubmitting(false);
      }
    },
    [refetch, handleCloseBorrowModal]
  );

  const actions = [
    {
      label: "Edit",
      handler: handleOpenEditModal,
      color: "warning",
    },
    {
      label: "Borrow",
      handler: handleBorrow,
      disabled: (row) => !row.available,
      color: "primary",
    },
  ];

  return (
    <Container maxWidth="lg">
      <Box sx={{ mt: 4, pb: 10 }}>
        <Box
          sx={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            mb: 3,
          }}
        >
          <Typography variant="h4">Books</Typography>
          <Button
            variant="contained"
            onClick={handleOpenAddModal}
            sx={{ textTransform: "none", fontSize: "1rem" }}
          >
            Add Book
          </Button>
        </Box>

        <PageStateHandler
          loading={loading}
          data={books}
          emptyMessage="No books available at the moment."
        >
          <DataTable
            columns={columns}
            rows={books}
            actions={actions}
          />
        </PageStateHandler>

        <Notification
          open={openFetchNotification}
          message={fetchError}
          type="error"
          onClose={() => setOpenFetchNotification(false)}
        />

        <Notification
          open={openNotification}
          message={notificationMessage}
          type={notificationType}
          onClose={() => setOpenNotification(false)}
        />

        {/* Book Form Modal for Add */}
        <BookFormModal
          open={openAddModal}
          onClose={handleCloseAddModal}
          onSubmit={handleAddBook}
          isLoading={isSubmitting}
        />

        {/* Book Form Modal for Edit */}
        <BookFormModal
          open={openEditModal}
          onClose={handleCloseEditModal}
          onSubmit={handleUpdateBook}
          isLoading={isSubmitting}
          editData={selectedBook}
        />

        {/* Borrow Form Modal */}
        <BorrowFormModal
          open={openBorrowModal}
          onClose={handleCloseBorrowModal}
          onSubmit={handleBorrowSubmit}
          isLoading={isBorrowSubmitting}
          book={selectedBookForBorrow}
        />
      </Box>
    </Container>
  );
};

export default BooksPage;
