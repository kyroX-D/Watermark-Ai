import Sidebar from "./Sidebar";
import { motion } from "framer-motion";

export default function DashboardLayout({ children }) {
  return (
    <div className="flex min-h-screen bg-gray-50 dark:bg-dark-bg">
      <Sidebar />
      <main className="flex-1 p-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
        >
          {children}
        </motion.div>
      </main>
    </div>
  );
}
