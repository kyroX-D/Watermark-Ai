import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { Toaster } from "react-hot-toast";
import { useEffect } from "react";

// Pages
import Home from "./pages/Home";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";
import CreateWatermark from "./pages/CreateWatermark";
import MyImages from "./pages/MyImages";
import Settings from "./pages/Settings";
import Pricing from "./pages/Pricing";
import AdminPanel from "./pages/AdminPanel";

// Components
import ProtectedRoute from "./components/common/ProtectedRoute";
import { useAuthStore } from "./hooks/useAuth";

function App() {
  const { checkAuth } = useAuthStore();

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  return (
    <Router>
      <div className="min-h-screen bg-gray-50 dark:bg-dark-bg text-gray-900 dark:text-gray-100 transition-colors">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/pricing" element={<Pricing />} />

          {/* Protected Routes */}
          <Route element={<ProtectedRoute />}>
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/create" element={<CreateWatermark />} />
            <Route path="/my-images" element={<MyImages />} />
            <Route path="/settings" element={<Settings />} />
            <Route path="/admin" element={<AdminPanel />} />
          </Route>
        </Routes>

        <Toaster
          position="top-right"
          toastOptions={{
            className: "dark:bg-dark-surface dark:text-white",
            style: {
              background: "#333",
              color: "#fff",
            },
          }}
        />
      </div>
    </Router>
  );
}

export default App;