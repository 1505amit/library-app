import { Container, Typography, Box } from "@mui/material";
import DataTable from "../components/DataTable";
import PageStateHandler from "../components/PageStateHandler";
import Notification from "../components/Notification";
import { useDataFetch } from "../hooks/useDataFetch";
import { getMembers } from "../api/members";

const MembersPage = () => {
  const { data: members, loading, error: fetchError, openSnackbar: openFetchNotification, setOpenSnackbar: setOpenFetchNotification } =
    useDataFetch(getMembers);

  const columns = [
    { field: "id", headerName: "ID" },
    { field: "name", headerName: "Name" },
    { field: "email", headerName: "Email" },
    { field: "phone", headerName: "Phone" },
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

export default MembersPage;
