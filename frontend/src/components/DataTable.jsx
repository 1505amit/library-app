import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Button,
  Box
} from "@mui/material";

const DataTable = ({ columns, rows, onAction, actions = [] }) => {
  // Support both single action (legacy) and multiple actions
  const actionList = onAction 
    ? [{ label: onAction.label, handler: onAction.handler, disabled: onAction.disabled, color: "primary" }]
    : actions;

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
          {rows.map((row) => (
            <TableRow key={row.id}>
              {columns.map((col) => {
                const value = col.field.split('.').reduce((acc, key) => acc[key], row);
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
                        disabled={action.disabled ? action.disabled(row) : false}
                      >
                        {action.label}
                      </Button>
                    ))}
                  </Box>
                </TableCell>
              )}
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
}

export default DataTable;
