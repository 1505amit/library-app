import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Button
} from "@mui/material";

const DataTable = ({ columns, rows, onAction }) => {
  return (
    <TableContainer component={Paper}>
      <Table>
        <TableHead>
          <TableRow>
            {columns.map((col) => (
              <TableCell key={col.field}>{col.headerName}</TableCell>
            ))}
            {onAction && <TableCell>Action</TableCell>}
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
              {onAction && (
                <TableCell>
                  <Button
                    variant="contained"
                    color="primary"
                    size="small"
                    onClick={() => onAction.handler(row)}
                    disabled={onAction.disabled ? onAction.disabled(row) : false}
                  >
                    {onAction.label || "Action"}
                  </Button>
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
