import { useCallback, useState } from "react";
import { Container, Typography, Box, Chip, Button } from "@mui/material";
import DataTable from "../components/DataTable";
import PageStateHandler from "../components/PageStateHandler";
import Notification from "../components/Notification";
import BookFormModal from "../components/BookFormModal";
import { useDataFetch } from "../hooks/useDataFetch";
import { getBooks, createBook } from "../api/books";

const BooksPage = () => {
  const { data: books, loading, error: fetchError, openSnackbar: openFetchNotification, setOpenSnackbar: setOpenFetchNotification, refetch } =
    useDataFetch(getBooks);
  
  const [openAddModal, setOpenAddModal] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
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
      headerName: "Available",
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

  // Handle borrow action
  const handleBorrow = useCallback((book) => {
    console.log(`Borrowing book: ${book.title}`);
    // TODO: integrate with borrow API
  }, []);

  return (
    <Container maxWidth="lg">
      <Box sx={{ mt: 4 }}>
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
            onAction={{
              label: "Borrow",
              handler: handleBorrow,
              disabled: (row) => !row.available,
            }}
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
      </Box>
    </Container>
  );
};

export default BooksPage;
