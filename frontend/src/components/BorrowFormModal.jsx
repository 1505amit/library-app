import { useCallback, useState, useEffect } from "react";
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Box,
  CircularProgress,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Typography,
  Grid,
} from "@mui/material";
import { getMembers } from "../api/members";
import { getBooks } from "../api/books";

const INITIAL_FORM_STATE = {
  member_id: "",
  book_id: "",
};

const INITIAL_ERRORS = {
  member_id: "",
  book_id: "",
};

const BorrowFormModal = ({
  open,
  onClose,
  onSubmit,
  isLoading = false,
  book = null, // Optional: when provided, only member dropdown is shown
}) => {
  const [formData, setFormData] = useState(INITIAL_FORM_STATE);
  const [errors, setErrors] = useState(INITIAL_ERRORS);
  const [touched, setTouched] = useState({});
  const [members, setMembers] = useState([]);
  const [books, setBooks] = useState([]);
  const [loadingOptions, setLoadingOptions] = useState(false);
  const [loadError, setLoadError] = useState("");

  // Load members and books when modal opens
  useEffect(() => {
    if (open) {
      const loadData = async () => {
        setLoadingOptions(true);
        try {
          const [membersData, booksData] = await Promise.all([
            getMembers(1, 100), // Fetch with high limit to get all members
            book ? Promise.resolve(null) : getBooks(1, 100), // Fetch with high limit to get all books
          ]);
          
          // Extract data arrays from paginated responses
          const membersList = membersData.data || membersData || [];
          const booksList = booksData?.data || booksData || [];
          
          // Filter active members and available books
          const activeMembers = membersList.filter((m) => m.active);
          setMembers(activeMembers);

          // Only set available books if not in single-book mode
          if (!book && booksList.length > 0) {
            const availableBooks = booksList.filter((b) => b.available);
            setBooks(availableBooks);
          }

          // If book is provided, set it in form data
          if (book) {
            setFormData({ member_id: "", book_id: book.id });
          }

          setLoadError("");
        } catch (error) {
          console.error("Error loading form data:", error);
          setLoadError("Failed to load form data");
        } finally {
          setLoadingOptions(false);
        }
      };

      loadData();
      // Reset form
      if (!book) {
        setFormData({ ...INITIAL_FORM_STATE });
      }
      setErrors(INITIAL_ERRORS);
      setTouched({});
    }
  }, [open, book]);

  // Validate form field
  const validateField = useCallback((name, value) => {
    switch (name) {
      case "member_id":
        return !value ? "Please select a member" : "";
      case "book_id":
        return !value ? "Please select a book" : "";
      default:
        return "";
    }
  }, []);

  // Handle input change with validation
  const handleInputChange = useCallback(
    (e) => {
      const { name, value } = e.target;
      const newFormData = { ...formData, [name]: value };
      setFormData(newFormData);

      // Validate if field has been touched
      if (touched[name]) {
        const error = validateField(name, value);
        setErrors({ ...errors, [name]: error });
      }
    },
    [formData, touched, validateField, errors]
  );

  // Handle field blur
  const handleBlur = useCallback(
    (e) => {
      const { name } = e.target;
      setTouched({ ...touched, [name]: true });
      const error = validateField(name, formData[name]);
      setErrors({ ...errors, [name]: error });
    },
    [formData, touched, validateField, errors]
  );

  // Handle form submission
  const handleSubmit = useCallback(async () => {
    // Mark all fields as touched
    const fieldsToCheck = { member_id: true };
    if (!book) {
      fieldsToCheck.book_id = true;
    }
    setTouched(fieldsToCheck);

    // Validate all fields
    const memberError = validateField("member_id", formData.member_id);
    const newErrors = { member_id: memberError };

    if (!book) {
      const bookError = validateField("book_id", formData.book_id);
      newErrors.book_id = bookError;
    }
    setErrors(newErrors);

    // Check if form is valid
    const isValid = book
      ? memberError === ""
      : memberError === "" && newErrors.book_id === "";

    if (isValid) {
      try {
        const borrowData = {
          member_id: parseInt(formData.member_id),
          book_id: book ? book.id : parseInt(formData.book_id),
        };
        await onSubmit(borrowData);
        // Reset form on success
        setFormData({ ...INITIAL_FORM_STATE });
        setTouched({});
      } catch (error) {
        console.error("Error submitting form:", error);
        // Error is handled by parent component
      }
    }
  }, [formData, validateField, onSubmit, book]);

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>Create Borrow Record</DialogTitle>
      <DialogContent>
        <Box sx={{ pt: 2, display: "flex", flexDirection: "column", gap: 2 }}>
          {/* Error message */}
          {loadError && (
            <Typography color="error" variant="body2">
              {loadError}
            </Typography>
          )}

          {/* Book Info - only show when book is provided */}
          {book && (
            <Box sx={{ p: 2, backgroundColor: "#f5f5f5", borderRadius: 1 }}>
              <Box sx={{ display: "flex", gap: 1, mb: 1 }}>
                <Typography variant="body1" color="textSecondary">
                  Book:
                </Typography>
                <Typography variant="body1" sx={{ fontWeight: 600 }}>
                  {book.title}
                </Typography>
              </Box>
              <Box sx={{ display: "flex", gap: 1 }}>
                <Typography variant="body1" color="textSecondary">
                  Author:
                </Typography>
                <Typography variant="body1" sx={{ fontWeight: 600 }}>
                  {book.author}
                </Typography>
              </Box>
            </Box>
          )}

          {/* Member Dropdown */}
          <FormControl fullWidth disabled={loadingOptions}>
            <InputLabel id="member-select-label">Member</InputLabel>
            <Select
              labelId="member-select-label"
              id="member-select"
              name="member_id"
              value={formData.member_id}
              onChange={handleInputChange}
              onBlur={handleBlur}
              label="Member"
              error={touched.member_id && !!errors.member_id}
            >
              <MenuItem value="">
                <em>Select a member</em>
              </MenuItem>
              {members.map((member) => (
                <MenuItem key={member.id} value={member.id}>
                  {member.name} ({member.email})
                </MenuItem>
              ))}
            </Select>
            {touched.member_id && errors.member_id && (
              <Typography variant="caption" color="error">
                {errors.member_id}
              </Typography>
            )}
          </FormControl>

          {/* Book Dropdown - only show when book is not provided */}
          {!book && (
            <FormControl fullWidth disabled={loadingOptions}>
              <InputLabel id="book-select-label">Book</InputLabel>
              <Select
                labelId="book-select-label"
                id="book-select"
                name="book_id"
                value={formData.book_id}
                onChange={handleInputChange}
                onBlur={handleBlur}
                label="Book"
                error={touched.book_id && !!errors.book_id}
              >
                <MenuItem value="">
                  <em>Select a book</em>
                </MenuItem>
                {books.map((book) => (
                  <MenuItem key={book.id} value={book.id}>
                    {book.title}
                  </MenuItem>
                ))}
              </Select>
              {touched.book_id && errors.book_id && (
                <Typography variant="caption" color="error">
                  {errors.book_id}
                </Typography>
              )}
            </FormControl>
          )}
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} disabled={isLoading || loadingOptions}>
          Cancel
        </Button>
        <Button
          onClick={handleSubmit}
          variant="contained"
          disabled={isLoading || loadingOptions}
          sx={{ position: "relative" }}
        >
          {isLoading ? (
            <>
              <CircularProgress
                size={24}
                sx={{
                  position: "absolute",
                  left: "50%",
                  marginLeft: "-12px",
                }}
              />
              <span style={{ visibility: "hidden" }}>Borrow</span>
            </>
          ) : (
            "Borrow"
          )}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default BorrowFormModal;
