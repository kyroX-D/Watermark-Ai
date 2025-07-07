import { create } from "zustand";
import { persist } from "zustand/middleware";

export const useTheme = create(
  persist(
    (set, get) => ({
      theme: "light",

      toggleTheme: () => {
        const newTheme = get().theme === "light" ? "dark" : "light";
        set({ theme: newTheme });

        // Update document class
        if (newTheme === "dark") {
          document.documentElement.classList.add("dark");
        } else {
          document.documentElement.classList.remove("dark");
        }
      },

      initTheme: () => {
        const theme = get().theme;
        if (theme === "dark") {
          document.documentElement.classList.add("dark");
        }
      },
    }),
    {
      name: "theme-storage",
    },
  ),
);

// Initialize theme on load
if (typeof window !== "undefined") {
  const theme = useTheme.getState().theme;
  if (theme === "dark") {
    document.documentElement.classList.add("dark");
  }
}
