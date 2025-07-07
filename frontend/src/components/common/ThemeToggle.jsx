import { Sun, Moon } from "lucide-react";
import { useTheme } from "../../hooks/useTheme";
import { motion } from "framer-motion";

export default function ThemeToggle() {
  const { theme, toggleTheme } = useTheme();

  return (
    <motion.button
      whileTap={{ scale: 0.95 }}
      onClick={toggleTheme}
      className="p-2 rounded-lg bg-gray-100 dark:bg-dark-surface hover:bg-gray-200 dark:hover:bg-dark-border transition-colors"
    >
      {theme === "dark" ? (
        <Sun className="w-5 h-5 text-yellow-500" />
      ) : (
        <Moon className="w-5 h-5 text-gray-700" />
      )}
    </motion.button>
  );
}
