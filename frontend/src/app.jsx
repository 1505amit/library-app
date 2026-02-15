import { BrowserRouter, Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";
import ProtectedRoute from "./components/ProtectedRoute";
import ErrorBoundary from "./components/ErrorBoundary";
import { AuthProvider } from "./context/AuthContext";
import { ROUTES } from "./config/routes";

const App = () => {
  return (
    <ErrorBoundary>
      <AuthProvider>
        <BrowserRouter>
          <Navbar />
          <Routes>
          {ROUTES.map((route) => {
            const { path, component: Component, isProtected } = route;
            return (
              <Route
                key={path}
                path={path}
                element={
                  isProtected ? (
                    <ProtectedRoute>
                      <Component />
                    </ProtectedRoute>
                  ) : (
                    <Component />
                  )
                }
              />
            );
          })}
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </ErrorBoundary>
  );
};

export default App;
