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
} from "@mui/material";

const INITIAL_FORM_STATE = {
  title: "",
  author: "",
  published_year: new Date().getFullYear(),
};

const INITIAL_ERRORS = {
  title: "",
  author: "",
  published_year: "",
};

const BookFormModal = ({
  open,
  onClose,
  onSubmit,
  isLoading = false,
  editData = null,
}) => {
  const [formData, setFormData] = useState(INITIAL_FORM_STATE);
  const [errors, setErrors] = useState(INITIAL_ERRORS);
  const [touched, setTouched] = useState({});

  // Initialize form when modal opens
  useEffect(() => {
    if (open) {
      if (editData) {
        // For edit mode, populate form with existing data
        setFormData({
          title: editData.title,
          author: editData.author,
          published_year: editData.published_year,
        });
      } else {
        // For add mode, reset to initial state
        setFormData({ ...INITIAL_FORM_STATE });
      }
      setErrors(INITIAL_ERRORS);
      setTouched({});
    }
  }, [open, editData]);

  // Validate form field
  const validateField = useCallback((name, value) => {
    const newErrors = { ...errors };

    switch (name) {
      case "title":
        if (!value.trim()) {
          newErrors.title = "Title is required";
        } else if (value.trim().length < 2) {
          newErrors.title = "Title must be at least 2 characters long";
        } else {
          newErrors.title = "";
        }
        break;

      case "author":
        if (!value.trim()) {
          newErrors.author = "Author is required";
        } else if (value.trim().length < 2) {
          newErrors.author = "Author must be at least 2 characters long";
        } else {
          newErrors.author = "";
        }
        break;

      case "published_year":
        const year = parseInt(value, 10);
        if (value && (isNaN(year) || year < 1000 || year > new Date().getFullYear())) {
          newErrors.published_year = `Year must be between 1000 and ${new Date().getFullYear()}`;
        } else {
          newErrors.published_year = "";
        }
        break;

      default:
        break;
    }

    return newErrors;
  }, [errors]);

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
      const newErrors = validateField(name, inputValue);
      setErrors(newErrors);
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

    if (!formData.title.trim()) {
      newErrors.title = "Title is required";
    } else if (formData.title.trim().length < 2) {
      newErrors.title = "Title must be at least 2 characters long";
    }

    if (!formData.author.trim()) {
      newErrors.author = "Author is required";
    } else if (formData.author.trim().length < 2) {
      newErrors.author = "Author must be at least 2 characters long";
    }

    if (
      formData.published_year &&
      (isNaN(parseInt(formData.published_year, 10)) ||
        formData.published_year < 1000 ||
        formData.published_year > new Date().getFullYear())
    ) {
      newErrors.published_year = `Year must be between 1000 and ${new Date().getFullYear()}`;
    }

    return Object.values(newErrors).every((error) => error === "");
  }, [formData]);

  // Handle form submission
  const handleSubmit = useCallback(() => {
    // Mark all fields as touched for validation
    setTouched({
      title: true,
      author: true,
      published_year: true,
      available: true,
    });

    // Validate all fields
    let newErrors = { ...INITIAL_ERRORS };

    if (!formData.title.trim()) {
      newErrors.title = "Title is required";
    } else if (formData.title.trim().length < 2) {
      newErrors.title = "Title must be at least 2 characters long";
    }

    if (!formData.author.trim()) {
      newErrors.author = "Author is required";
    } else if (formData.author.trim().length < 2) {
      newErrors.author = "Author must be at least 2 characters long";
    }

    if (
      formData.published_year &&
      (isNaN(parseInt(formData.published_year, 10)) ||
        formData.published_year < 1000 ||
        formData.published_year > new Date().getFullYear())
    ) {
      newErrors.published_year = `Year must be between 1000 and ${new Date().getFullYear()}`;
    }

    setErrors(newErrors);

    if (Object.values(newErrors).every((error) => error === "")) {
      // Prepare data for submission
      const submissionData = {
        ...formData,
        published_year: formData.published_year
          ? parseInt(formData.published_year, 10)
          : null,
      };

      onSubmit(submissionData);
    }
  }, [formData, onSubmit]);

  // Handle modal close - cleanup state
  const handleClose = useCallback(() => {
    // Reset form state to prevent memory leaks
    setFormData(INITIAL_FORM_STATE);
    setErrors(INITIAL_ERRORS);
    setTouched({});
    onClose();
  }, [onClose]);

  const isEditMode = !!editData;
  const title = isEditMode ? "Edit Book" : "Add New Book";

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
      <DialogTitle sx={{ fontWeight: 600 }}>{title}</DialogTitle>
      <DialogContent sx={{ pt: 3 }}>
        <Box sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
          {/* Title Field */}
          <TextField
            fullWidth
            label="Title"
            name="title"
            value={formData.title}
            onChange={handleInputChange}
            onBlur={handleBlur}
            error={Boolean(touched.title && errors.title)}
            helperText={touched.title && errors.title}
            placeholder="Enter book title"
            disabled={isLoading}
            autoFocus
            variant="outlined"
          />

          {/* Author Field */}
          <TextField
            fullWidth
            label="Author"
            name="author"
            value={formData.author}
            onChange={handleInputChange}
            onBlur={handleBlur}
            error={Boolean(touched.author && errors.author)}
            helperText={touched.author && errors.author}
            placeholder="Enter author name"
            disabled={isLoading}
            variant="outlined"
          />

          {/* Published Year Field */}
          <TextField
            fullWidth
            label="Published Year"
            name="published_year"
            type="number"
            value={formData.published_year || ""}
            onChange={handleInputChange}
            onBlur={handleBlur}
            error={Boolean(touched.published_year && errors.published_year)}
            helperText={touched.published_year && errors.published_year}
            placeholder={`e.g., ${new Date().getFullYear()}`}
            disabled={isLoading}
            inputProps={{
              min: 1000,
              max: new Date().getFullYear(),
            }}
            variant="outlined"
          />
        </Box>
      </DialogContent>

      <DialogActions sx={{ p: 2, gap: 1 }}>
        <Button
          onClick={handleClose}
          disabled={isLoading}
          sx={{
            textTransform: "none",
            fontSize: "1rem",
          }}
        >
          Cancel
        </Button>
        <Button
          onClick={handleSubmit}
          disabled={isLoading || !isFormValid}
          variant="contained"
          sx={{
            textTransform: "none",
            fontSize: "1rem",
          }}
        >
          {isLoading ? (
            <>
              <CircularProgress size={20} sx={{ mr: 1 }} />
              {isEditMode ? "Updating..." : "Adding..."}
            </>
          ) : (
            isEditMode ? "Update Book" : "Add Book"
          )}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default BookFormModal;
