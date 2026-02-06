import { Container, Typography, Box, Chip } from "@mui/material";
import DataTable from "../components/DataTable";
import PageStateHandler from "../components/PageStateHandler";
import ErrorSnackbar from "../components/ErrorSnackbar";
import { useDataFetch } from "../hooks/useDataFetch";
import { getBooks } from "../api/books";

const BooksPage = () => {
  const { data: books, loading, error, openSnackbar, setOpenSnackbar } =
    useDataFetch(getBooks);

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

  const handleBorrow = (book) => {
    console.log(`Borrowing book: ${book.title}`);
    // TODO: integrate with borrow API
  };

  return (
    <Container maxWidth="lg">
      <Box sx={{ mt: 4 }}>
        <Typography variant="h4" gutterBottom>
          Books
        </Typography>

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

        <ErrorSnackbar
          open={openSnackbar}
          message={error}
          onClose={() => setOpenSnackbar(false)}
        />
      </Box>
    </Container>
  );
};

export default BooksPage;
