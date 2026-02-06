import { AppBar, Toolbar, Typography, Button } from "@mui/material";
import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const Navbar = () => {
  const { isAuthenticated, logout } = useAuth();

  return (
    <AppBar position="static">
      <Toolbar>
        <Typography variant="h6" sx={{ flexGrow: 1 }}>
          Library App
        </Typography>
        {isAuthenticated && (
          <>
            <Button color="inherit" component={Link} to="/books">Books</Button>
            <Button color="inherit" component={Link} to="/members">Members</Button>
            <Button color="inherit" component={Link} to="/borrow">Borrow</Button>
            <Button color="inherit" onClick={logout}>Logout</Button>
          </>
        )}
      </Toolbar>
    </AppBar>
  );
};

export default Navbar;
