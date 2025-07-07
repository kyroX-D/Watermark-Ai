import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Image, Droplets, Calendar, TrendingUp } from "lucide-react";
import DashboardLayout from "../components/dashboard/DashboardLayout";
import { useAuthStore } from "../hooks/useAuth";
import api from "../services/api";

export default function Dashboard() {
  const { user, token } = useAuthStore();
  const [stats, setStats] = useState({
    totalImages: 0,
    todayImages: 0,
    remainingToday: 2,
    subscription: "free",
  });

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const response = await api.get("/users/stats", {
        headers: { Authorization: `Bearer ${token}` },
      });
      setStats(response.data);
    } catch (error) {
      console.error("Failed to fetch stats:", error);
    }
  };

  const statCards = [
    {
      title: "Total Watermarks",
      value: stats.totalImages,
      icon: Image,
      color: "text-blue-600",
      bgColor: "bg-blue-100 dark:bg-blue-900/20",
    },
    {
      title: "Created Today",
      value: stats.todayImages,
      icon: Calendar,
      color: "text-green-600",
      bgColor: "bg-green-100 dark:bg-green-900/20",
    },
    {
      title: "Remaining Today",
      value:
        user?.subscription_tier === "free"
          ? `${stats.remainingToday}/2`
          : "Unlimited",
      icon: Droplets,
      color: "text-purple-600",
      bgColor: "bg-purple-100 dark:bg-purple-900/20",
    },
    {
      title: "Subscription",
      value: user?.subscription_tier?.toUpperCase() || "FREE",
      icon: TrendingUp,
      color: "text-orange-600",
      bgColor: "bg-orange-100 dark:bg-orange-900/20",
    },
  ];

  return (
    <DashboardLayout>
      <div>
        <h1 className="text-3xl font-bold mb-8">
          Welcome back, {user?.username || "User"}!
        </h1>

        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {statCards.map((stat, index) => (
            <motion.div
              key={stat.title}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="card p-6"
            >
              <div className="flex items-center justify-between mb-4">
                <div className={`p-3 rounded-lg ${stat.bgColor}`}>
                  <stat.icon className={`w-6 h-6 ${stat.color}`} />
                </div>
              </div>
              <h3 className="text-2xl font-bold mb-1">{stat.value}</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                {stat.title}
              </p>
            </motion.div>
          ))}
        </div>

        <div className="grid lg:grid-cols-2 gap-8">
          <div className="card p-6">
            <h2 className="text-xl font-semibold mb-4">Quick Actions</h2>
            <div className="space-y-3">
              <a
                href="/create"
                className="block p-4 bg-primary-50 dark:bg-primary-900/20 rounded-lg hover:bg-primary-100 dark:hover:bg-primary-900/30 transition-colors"
              >
                <h3 className="font-semibold text-primary-600 dark:text-primary-400">
                  Create New Watermark
                </h3>
                <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                  Upload an image and add AI-powered watermarks
                </p>
              </a>

              <a
                href="/my-images"
                className="block p-4 bg-gray-50 dark:bg-dark-bg rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
              >
                <h3 className="font-semibold">View Your Images</h3>
                <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                  Browse and manage your watermarked images
                </p>
              </a>
            </div>
          </div>

          <div className="card p-6">
            <h2 className="text-xl font-semibold mb-4">Subscription Status</h2>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-gray-600 dark:text-gray-400">
                  Current Plan
                </span>
                <span className="font-semibold">
                  {user?.subscription_tier?.toUpperCase()}
                </span>
              </div>

              {user?.subscription_tier === "free" && (
                <>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-600 dark:text-gray-400">
                      Daily Limit
                    </span>
                    <span className="font-semibold">2 watermarks</span>
                  </div>

                  <div className="pt-4">
                    <a
                      href="/pricing"
                      className="btn-primary w-full text-center"
                    >
                      Upgrade to Pro
                    </a>
                    <p className="text-sm text-gray-500 dark:text-gray-400 text-center mt-2">
                      Get unlimited watermarks and higher resolution
                    </p>
                  </div>
                </>
              )}

              {user?.subscription_end_date && (
                <div className="flex justify-between items-center">
                  <span className="text-gray-600 dark:text-gray-400">
                    Renews on
                  </span>
                  <span className="font-semibold">
                    {new Date(user.subscription_end_date).toLocaleDateString()}
                  </span>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
