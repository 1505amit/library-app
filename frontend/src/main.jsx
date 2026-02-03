import React from "react";
import ReactDOM from "react-dom/client";
import App from "./app";
import CssBaseline from "@mui/material/CssBaseline";

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    {/* CssBaseline gives MUI a consistent baseline for styles */}
    <CssBaseline />
    <App />
  </React.StrictMode>
);
