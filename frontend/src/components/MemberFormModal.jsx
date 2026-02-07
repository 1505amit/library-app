import { useCallback, useMemo, useState, useEffect } from "react";
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  Box,
  CircularProgress,
  FormControlLabel,
  Checkbox,
} from "@mui/material";

const INITIAL_FORM_STATE = {
  name: "",
  email: "",
  phone: "",
  active: true,
};

const INITIAL_ERRORS = {
  name: "",
  email: "",
  phone: "",
};

const MemberFormModal = ({
  open,
  onClose,
  onSubmit,
  isLoading = false,
}) => {
  const [formData, setFormData] = useState(INITIAL_FORM_STATE);
  const [errors, setErrors] = useState(INITIAL_ERRORS);
  const [touched, setTouched] = useState({});

  // Initialize form when modal opens
  useEffect(() => {
    if (open) {
      // Reset form for adding new member
      setFormData({ ...INITIAL_FORM_STATE });
      setErrors(INITIAL_ERRORS);
      setTouched({});
    }
  }, [open]);

  // Email validation helper
  const isValidEmail = useCallback((email) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }, []);

  // Phone validation helper - basic validation
  const isValidPhone = useCallback((phone) => {
    if (!phone) return true; // Phone is optional
    const phoneRegex = /^[\d\s\-\+\(\)]+$/;
    return phoneRegex.test(phone) && phone.length >= 10;
  }, []);

  // Validate form field
  const validateField = useCallback((name, value) => {
    const newErrors = { ...errors };

    switch (name) {
      case "name":
        if (!value.trim()) {
          newErrors.name = "Name is required";
        } else if (value.trim().length < 2) {
          newErrors.name = "Name must be at least 2 characters long";
        } else {
          newErrors.name = "";
        }
        break;

      case "email":
        if (!value.trim()) {
          newErrors.email = "Email is required";
        } else if (!isValidEmail(value.trim())) {
          newErrors.email = "Please enter a valid email address";
        } else {
          newErrors.email = "";
        }
        break;

      case "phone":
        if (value && !isValidPhone(value)) {
          newErrors.phone = "Phone must be at least 10 characters and contain only digits, spaces, or +() -";
        } else {
          newErrors.phone = "";
        }
        break;

      default:
        break;
    }

    return newErrors;
  }, [errors, isValidEmail, isValidPhone]);

  // Handle input change with validation
  const handleInputChange = useCallback(
    (e) => {
      const { name, value, type, checked } = e.target;
      const inputValue = type === "checkbox" ? checked : value;

      setFormData((prev) => ({
        ...prev,
        [name]: inputValue,
      }));

      // Validate on change and update errors immediately
      if (name !== "active") {
        const newErrors = validateField(name, inputValue);
        setErrors(newErrors);
      }
    },
    [validateField]
  );

  // Handle blur event
  const handleBlur = useCallback((e) => {
    const { name } = e.target;
    setTouched((prev) => ({
      ...prev,
      [name]: true,
    }));
  }, []);

  // Validate entire form
  const isFormValid = useMemo(() => {
    const newErrors = { ...INITIAL_ERRORS };

    if (!formData.name.trim()) {
      newErrors.name = "Name is required";
    } else if (formData.name.trim().length < 2) {
      newErrors.name = "Name must be at least 2 characters long";
    }

    if (!formData.email.trim()) {
      newErrors.email = "Email is required";
    } else if (!isValidEmail(formData.email.trim())) {
      newErrors.email = "Please enter a valid email address";
    }

    if (formData.phone && !isValidPhone(formData.phone)) {
      newErrors.phone = "Phone must be at least 10 characters and contain only digits, spaces, or +() -";
    }

    return Object.values(newErrors).every((error) => error === "");
  }, [formData, isValidEmail, isValidPhone]);

  // Handle form submission
  const handleSubmit = useCallback(() => {
    // Mark all fields as touched for validation
    setTouched({
      name: true,
      email: true,
      phone: true,
    });

    // Validate all fields
    let newErrors = { ...INITIAL_ERRORS };

    if (!formData.name.trim()) {
      newErrors.name = "Name is required";
    } else if (formData.name.trim().length < 2) {
      newErrors.name = "Name must be at least 2 characters long";
    }

    if (!formData.email.trim()) {
      newErrors.email = "Email is required";
    } else if (!isValidEmail(formData.email.trim())) {
      newErrors.email = "Please enter a valid email address";
    }

    if (formData.phone && !isValidPhone(formData.phone)) {
      newErrors.phone = "Phone must be at least 10 characters and contain only digits, spaces, or +() -";
    }

    setErrors(newErrors);

    if (Object.values(newErrors).every((error) => error === "")) {
      // Prepare data for submission
      const submissionData = {
        name: formData.name.trim(),
        email: formData.email.trim(),
        phone: formData.phone?.trim() || null,
        active: formData.active,
      };

      onSubmit(submissionData);
    }
  }, [formData, onSubmit, isValidEmail, isValidPhone]);

  // Handle modal close - cleanup state to prevent memory leaks
  const handleClose = useCallback(() => {
    // Reset form state to prevent memory leaks
    setFormData(INITIAL_FORM_STATE);
    setErrors(INITIAL_ERRORS);
    setTouched({});
    onClose();
  }, [onClose]);

  return (
    <Dialog
      open={open}
      onClose={handleClose}
      maxWidth="sm"
      fullWidth
      PaperProps={{
        sx: {
          borderRadius: 2,
        },
      }}
    >
      <DialogTitle sx={{ fontWeight: 600 }}>Add New Member</DialogTitle>
      <DialogContent sx={{ pt: 3 }}>
        <Box sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
          {/* Name Field */}
          <TextField
            fullWidth
            label="Full Name"
            name="name"
            value={formData.name}
            onChange={handleInputChange}
            onBlur={handleBlur}
            error={Boolean(touched.name && errors.name)}
            helperText={touched.name && errors.name}
            placeholder="Enter member's full name"
            disabled={isLoading}
            autoFocus
            variant="outlined"
            inputProps={{
              maxLength: 255,
            }}
          />

          {/* Email Field */}
          <TextField
            fullWidth
            label="Email"
            name="email"
            type="email"
            value={formData.email}
            onChange={handleInputChange}
            onBlur={handleBlur}
            error={Boolean(touched.email && errors.email)}
            helperText={touched.email && errors.email}
            placeholder="Enter email address"
            disabled={isLoading}
            variant="outlined"
            inputProps={{
              maxLength: 255,
            }}
          />

          {/* Phone Field */}
          <TextField
            fullWidth
            label="Phone (Optional)"
            name="phone"
            value={formData.phone}
            onChange={handleInputChange}
            onBlur={handleBlur}
            error={Boolean(touched.phone && errors.phone)}
            helperText={touched.phone && errors.phone}
            placeholder="Enter phone number"
            disabled={isLoading}
            variant="outlined"
            inputProps={{
              maxLength: 20,
            }}
          />

          {/* Active Status */}
          <FormControlLabel
            control={
              <Checkbox
                name="active"
                checked={formData.active}
                onChange={handleInputChange}
                disabled={isLoading}
              />
            }
            label="Active Member"
          />
        </Box>
      </DialogContent>
      <DialogActions sx={{ p: 2, gap: 1 }}>
        <Button onClick={handleClose} disabled={isLoading}>
          Cancel
        </Button>
        <Button
          onClick={handleSubmit}
          variant="contained"
          disabled={!isFormValid || isLoading}
          sx={{
            minWidth: "120px",
            display: "flex",
            alignItems: "center",
            gap: 1,
          }}
        >
          {isLoading && <CircularProgress size={20} />}
          {isLoading ? "Adding..." : "Add Member"}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default MemberFormModal;
