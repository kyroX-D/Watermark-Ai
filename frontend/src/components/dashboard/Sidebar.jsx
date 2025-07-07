import { Link, useLocation } from "react-router-dom";
import { motion } from "framer-motion";
import {
  LayoutDashboard,
  Image,
  Droplets,
  Settings,
  CreditCard,
  LogOut,
} from "lucide-react";
import { useAuthStore } from "../../hooks/useAuth";

const menuItems = [
  { path: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { path: "/create", label: "Create Watermark", icon: Droplets },
  { path: "/my-images", label: "My Images", icon: Image },
  { path: "/pricing", label: "Subscription", icon: CreditCard },
  { path: "/settings", label: "Settings", icon: Settings },
];

export default function Sidebar() {
  const location = useLocation();
  const { logout } = useAuthStore();

  return (
    <aside className="w-64 min-h-screen bg-white dark:bg-dark-surface border-r border-gray-200 dark:border-dark-border">
      <div className="p-6">
        <Link to="/" className="flex items-center space-x-2 mb-8">
          <Droplets className="w-8 h-8 text-primary-600" />
          <span className="text-xl font-bold">AI Watermark</span>
        </Link>

        <nav className="space-y-2">
          {menuItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;

            return (
              <Link key={item.path} to={item.path} className="relative block">
                {isActive && (
                  <motion.div
                    layoutId="sidebar-indicator"
                    className="absolute inset-0 bg-primary-100 dark:bg-primary-900/20 rounded-lg"
                  />
                )}
                <div
                  className={`
                  relative flex items-center space-x-3 px-4 py-3 rounded-lg
                  transition-colors duration-200
                  ${
                    isActive
                      ? "text-primary-600 dark:text-primary-400"
                      : "text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200"
                  }
                `}
                >
                  <Icon className="w-5 h-5" />
                  <span className="font-medium">{item.label}</span>
                </div>
              </Link>
            );
          })}
        </nav>

        <div className="mt-8 pt-8 border-t border-gray-200 dark:border-dark-border">
          <button
            onClick={logout}
            className="flex items-center space-x-3 px-4 py-3 w-full rounded-lg
              text-gray-600 dark:text-gray-400 hover:text-red-600 dark:hover:text-red-400
              hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors"
          >
            <LogOut className="w-5 h-5" />
            <span className="font-medium">Logout</span>
          </button>
        </div>
      </div>
    </aside>
  );
}
