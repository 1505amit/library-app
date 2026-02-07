import { useCallback, useState } from "react";
import { Container, Typography, Box, Chip, Button } from "@mui/material";
import DataTable from "../components/DataTable";
import PageStateHandler from "../components/PageStateHandler";
import Notification from "../components/Notification";
import MemberFormModal from "../components/MemberFormModal";
import { useDataFetch } from "../hooks/useDataFetch";
import { getMembers, createMember } from "../api/members";

const MembersPage = () => {
  const { data: members, loading, error: fetchError, openSnackbar: openFetchNotification, setOpenSnackbar: setOpenFetchNotification, refetch } =
    useDataFetch(getMembers);
  
  const [openAddModal, setOpenAddModal] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [notificationMessage, setNotificationMessage] = useState("");
  const [openNotification, setOpenNotification] = useState(false);
  const [notificationType, setNotificationType] = useState("info");

  const columns = [
    { field: "id", headerName: "ID" },
    { field: "name", headerName: "Name" },
    { field: "email", headerName: "Email" },
    { field: "phone", headerName: "Phone" },
    {
      field: "active",
      headerName: "Status",
      render: (value) => (
        <Chip
          label={value ? "Active" : "Inactive"}
          color={value ? "success" : "error"}
          variant={value ? "success" : "error"}
          size="small"
        />
      ),
    },
  ];

  // Open add member modal
  const handleOpenAddModal = useCallback(() => {
    setOpenAddModal(true);
  }, []);

  // Close add member modal
  const handleCloseAddModal = useCallback(() => {
    setOpenAddModal(false);
  }, []);

  // Handle form submission for adding member
  const handleAddMember = useCallback(
    async (formData) => {
      setIsSubmitting(true);
      try {
        await createMember(formData);
        
        // Close modal
        handleCloseAddModal();
        
        // Refresh the members list
        await refetch();
        
        // Show success notification
        setNotificationMessage("Member added successfully!");
        setNotificationType("success");
        setOpenNotification(true);
      } catch (err) {
        console.error("Error adding member:", err);
        const errorMessage = 
          err.response?.data?.detail || "Failed to add member. Please try again.";
        setNotificationMessage(errorMessage);
        setNotificationType("error");
        setOpenNotification(true);
      } finally {
        setIsSubmitting(false);
      }
    },
    [handleCloseAddModal, refetch]
  );

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
          <Typography variant="h4">Members</Typography>
          <Button
            variant="contained"
            onClick={handleOpenAddModal}
            sx={{ textTransform: "none", fontSize: "1rem" }}
          >
            Add Member
          </Button>
        </Box>

        <PageStateHandler
          loading={loading}
          data={members}
          emptyMessage="No members available at the moment."
        >
          <DataTable
            columns={columns}
            rows={members}
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

        {/* Member Form Modal for Add */}
        <MemberFormModal
          open={openAddModal}
          onClose={handleCloseAddModal}
          onSubmit={handleAddMember}
          isLoading={isSubmitting}
        />
      </Box>
    </Container>
  );
};

export default MembersPage;
