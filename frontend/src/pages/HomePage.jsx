import { Container, Typography, Box, Paper } from "@mui/material";

export default function HomePage() {
  return (
    <Container maxWidth="md">
      <Box sx={{ mt: 4 }}>
        <Paper elevation={3} sx={{ p: 4 }}>
          <Typography variant="h3" gutterBottom>
            Welcome to the Neighborhood Library
          </Typography>
          <Typography variant="body1" paragraph>
            This is your admin dashboard. From here you can manage books,
            members, and borrow records. Use the navigation bar above to access
            different sections of the system.
          </Typography>
        </Paper>
      </Box>
    </Container>
  );
}
