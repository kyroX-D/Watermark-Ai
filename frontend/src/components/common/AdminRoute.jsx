// File: frontend/src/components/common/AdminRoute.jsx

import { Navigate, Outlet } from "react-router-dom";
import { useAuthStore } from "../../hooks/useAuth";

export default function AdminRoute() {
  const { isAuthenticated, isAdmin } = useAuthStore();

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (!isAdmin()) {
    return <Navigate to="/dashboard" replace />;
  }

  return <Outlet />;
}