import { useState } from "react";
import {
  Container,
  Typography,
  Box,
  Chip,
  FormControlLabel,
  Checkbox,
} from "@mui/material";
import DataTable from "../components/DataTable";
import PageStateHandler from "../components/PageStateHandler";
import Notification from "../components/Notification";
import { useDataFetch } from "../hooks/useDataFetch";
import { getBorrows } from "../api/borrow";
import { formatDateTime } from "../utils/dateFormatter";

const BorrowPage = () => {
  const [includeReturned, setIncludeReturned] = useState(true);
  const { data: borrows, loading, error: fetchError, openSnackbar: openFetchNotification, setOpenSnackbar: setOpenFetchNotification } =
    useDataFetch(() => getBorrows(includeReturned), [includeReturned]);

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
        <Typography variant="h4" gutterBottom>
          Borrowed Books
        </Typography>

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
