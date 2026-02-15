import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Button,
  Box,
  TablePagination,
} from "@mui/material";
import { useState, useEffect } from "react";

const DataTable = ({
  columns,
  rows,
  onAction,
  actions = [],
  totalRecords,
  onPaginationChange,
  pageSize,
  isServerPagination = false,
  currentPage = 1, // Accept current page from parent (1-indexed)
}) => {
  const [page, setPage] = useState(currentPage - 1); // Convert to 0-indexed for Material-UI
  const [rowsPerPage, setRowsPerPage] = useState(pageSize || 10);

  // Sync page state when currentPage or pageSize changes from parent
  useEffect(() => {
    setPage(Math.max(0, currentPage - 1)); // Ensure at least 0
  }, [currentPage]);

  // Sync rowsPerPage when pageSize changes
  useEffect(() => {
    setRowsPerPage(pageSize || 10);
  }, [pageSize]);

  // Support both single action (legacy) and multiple actions
  const actionList = onAction
    ? [{ label: onAction.label, handler: onAction.handler, disabled: onAction.disabled, color: "primary" }]
    : actions;

  // Handle pagination change (convert from 0-indexed to 1-indexed)
  const handleChangePage = (event, newPage) => {
    setPage(newPage);
    if (onPaginationChange) {
      onPaginationChange(newPage + 1, rowsPerPage); // Convert to 1-indexed for API
    }
  };

  // Handle rows per page change
  const handleChangeRowsPerPage = (event) => {
    const newRowsPerPage = parseInt(event.target.value, 10);
    setRowsPerPage(newRowsPerPage);
    setPage(0); // Reset to first page
    if (onPaginationChange) {
      onPaginationChange(1, newRowsPerPage); // Convert to 1-indexed for API
    }
  };

  return (
    <TableContainer component={Paper}>
      <Table>
        <TableHead>
          <TableRow>
            {columns.map((col) => (
              <TableCell key={col.field}>{col.headerName}</TableCell>
            ))}
            {actionList.length > 0 && <TableCell>Actions</TableCell>}
          </TableRow>
        </TableHead>
        <TableBody>
          {rows.length > 0 ? (
            rows.map((row) => (
              <TableRow key={row.id}>
                {columns.map((col) => {
                  const value = col.field
                    .split(".")
                    .reduce((acc, key) => acc[key], row);
                  return (
                    <TableCell key={col.field}>
                      {col.render ? col.render(value, row) : value}
                    </TableCell>
                  );
                })}
                {actionList.length > 0 && (
                  <TableCell>
                    <Box sx={{ display: "flex", gap: 1 }}>
                      {actionList.map((action, index) => (
                        <Button
                          key={index}
                          variant="contained"
                          color={action.color || "primary"}
                          size="small"
                          onClick={() => action.handler(row)}
                          disabled={
                            action.disabled ? action.disabled(row) : false
                          }
                        >
                          {action.label}
                        </Button>
                      ))}
                    </Box>
                  </TableCell>
                )}
              </TableRow>
            ))
          ) : (
            <TableRow>
              <TableCell
                colSpan={columns.length + (actionList.length > 0 ? 1 : 0)}
                align="center"
                sx={{ py: 3 }}
              >
                No records found
              </TableCell>
            </TableRow>
          )}
        </TableBody>
      </Table>
      {isServerPagination && (
        <TablePagination
          rowsPerPageOptions={[5, 10, 25, 50]}
          component="div"
          count={totalRecords || 0}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={handleChangePage}
          onRowsPerPageChange={handleChangeRowsPerPage}
        />
      )}
    </TableContainer>
  );
}

export default DataTable;
