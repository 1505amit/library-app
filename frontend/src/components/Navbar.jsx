import { AppBar, Toolbar, Typography, Button } from "@mui/material";
import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const Navbar = () => {
  const { isAuthenticated, logout } = useAuth();

  return (
    <AppBar position="sticky">
      <Toolbar>
        <Typography 
          variant="h6" 
          component={Link} 
          to="/" 
          sx={{ 
            mr: 7, 
            textDecoration: 'none', 
            color: 'inherit',
            '&:hover': {
              opacity: 0.8
            }
          }}
        >
          Library App
        </Typography>
        {isAuthenticated && (
          <>
            <Button color="inherit" component={Link} to="/books">Books</Button>
            <Button color="inherit" component={Link} to="/members">Members</Button>
            <Button color="inherit" component={Link} to="/borrow">Borrow Records</Button>
            <div style={{ flexGrow: 0.83 }} />
            <Button color="inherit" onClick={logout}>Logout</Button>
          </>
        )}
      </Toolbar>
    </AppBar>
  );
};

export default Navbar;
