import { useCallback, useState, useEffect } from "react";
import { Container, Typography, Box, Chip, Button } from "@mui/material";
import DataTable from "../components/DataTable";
import PageStateHandler from "../components/PageStateHandler";
import Notification from "../components/Notification";
import MemberFormModal from "../components/MemberFormModal";
import { usePaginatedDataFetch } from "../hooks/usePaginatedDataFetch";
import { getMembers, createMember, updateMember } from "../api/members";

const MembersPage = () => {
  const {
    data: members,
    totalRecords,
    page,
    pageSize,
    loading,
    error: fetchError,
    onPaginationChange,
    refetch,
  } = usePaginatedDataFetch(getMembers);

  const [openFetchNotification, setOpenFetchNotification] = useState(false);
  const [openAddModal, setOpenAddModal] = useState(false);
  const [openEditModal, setOpenEditModal] = useState(false);
  const [selectedMember, setSelectedMember] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [notificationMessage, setNotificationMessage] = useState("");
  const [openNotification, setOpenNotification] = useState(false);
  const [notificationType, setNotificationType] = useState("info");

  // Show error notification when fetch fails (filter out AbortError from Strict Mode)
  useEffect(() => {
    // Only show error notification if there's a real error (not AbortError or empty)
    if (fetchError && fetchError.trim() && !fetchError.includes("aborted") && !fetchError.includes("canceled")) {
      setOpenFetchNotification(true);
    }
  }, [fetchError]);

  const columns = [
    { field: "id", headerName: "Sr. No." },
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

  // Open edit member modal
  const handleOpenEditModal = useCallback((member) => {
    setSelectedMember(member);
    setOpenEditModal(true);
  }, []);

  // Close edit member modal
  const handleCloseEditModal = useCallback(() => {
    setOpenEditModal(false);
    setSelectedMember(null);
  }, []);

  // Handle form submission for adding member
  const handleAddMember = useCallback(
    async (formData) => {
      const controller = new AbortController();
      const signal = controller.signal;

      setIsSubmitting(true);
      try {
        await createMember(formData, signal);
        
        // Close modal
        handleCloseAddModal();
        
        // Refresh the members list
        await refetch();
        
        // Show success notification
        setNotificationMessage("Member added successfully!");
        setNotificationType("success");
        setOpenNotification(true);
      } catch (err) {
        // Ignore abort errors
        if (err.name === "AbortError") {
          return;
        }
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

  // Handle form submission for updating member
  const handleUpdateMember = useCallback(
    async (formData) => {
      const controller = new AbortController();
      const signal = controller.signal;

      setIsSubmitting(true);
      try {
        await updateMember(selectedMember.id, formData, signal);
        
        // Close modal
        handleCloseEditModal();
        
        // Refresh the members list
        await refetch();
        
        // Show success notification
        setNotificationMessage("Member updated successfully!");
        setNotificationType("success");
        setOpenNotification(true);
      } catch (err) {
        // Ignore abort errors
        if (err.name === "AbortError") {
          return;
        }
        console.error("Error updating member:", err);
        const errorMessage = 
          err.response?.data?.detail || "Failed to update member. Please try again.";
        setNotificationMessage(errorMessage);
        setNotificationType("error");
        setOpenNotification(true);
      } finally {
        setIsSubmitting(false);
      }
    },
    [selectedMember, handleCloseEditModal, refetch]
  );

  const actions = [
    {
      label: "Edit",
      handler: handleOpenEditModal,
      color: "warning",
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
            actions={actions}
            totalRecords={totalRecords}
            onPaginationChange={onPaginationChange}
            pageSize={pageSize}
            isServerPagination={true}
            currentPage={page}
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

        {/* Member Form Modal for Edit */}
        <MemberFormModal
          open={openEditModal}
          onClose={handleCloseEditModal}
          onSubmit={handleUpdateMember}
          isLoading={isSubmitting}
          editData={selectedMember}
        />
      </Box>
    </Container>
  );
};

export default MembersPage;
