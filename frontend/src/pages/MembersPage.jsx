import { Container, Typography, Box } from "@mui/material";
import DataTable from "../components/DataTable";
import PageStateHandler from "../components/PageStateHandler";
import ErrorSnackbar from "../components/ErrorSnackbar";
import { useDataFetch } from "../hooks/useDataFetch";
import { getMembers } from "../api/members";

const MembersPage = () => {
  const { data: members, loading, error, openSnackbar, setOpenSnackbar } =
    useDataFetch(getMembers);

  const columns = [
    { field: "id", headerName: "ID" },
    { field: "name", headerName: "Name" },
    { field: "email", headerName: "Email" },
    { field: "phone", headerName: "Phone" },
    { field: "membership_date", headerName: "Member Since" },
  ];

  const handleEdit = (member) => {
    console.log(`Editing member: ${member.name}`);
    // TODO: integrate with edit API
  };

  return (
    <Container maxWidth="lg">
      <Box sx={{ mt: 4 }}>
        <Typography variant="h4" gutterBottom>
          Members
        </Typography>

        <PageStateHandler
          loading={loading}
          data={members}
          emptyMessage="No members available at the moment."
        >
          <DataTable
            columns={columns}
            rows={members}
            onAction={{
              label: "Edit",
              handler: handleEdit,
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

export default MembersPage;
