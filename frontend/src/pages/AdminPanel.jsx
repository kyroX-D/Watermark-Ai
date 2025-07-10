// File: frontend/src/pages/AdminPanel.jsx

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { 
  Users, CreditCard, Image, TrendingUp, Gift, Search, 
  Loader, Calendar, Mail, Shield, AlertCircle 
} from "lucide-react";
import { useNavigate } from "react-router-dom";
import toast from "react-hot-toast";

import DashboardLayout from "../components/dashboard/DashboardLayout";
import { useAuthStore } from "../hooks/useAuth";
import api from "../services/api";

export default function AdminPanel() {
  const navigate = useNavigate();
  const { user, token, isAdmin } = useAuthStore();
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("overview");
  const [stats, setStats] = useState({
    total_users: 0,
    free_users: 0,
    pro_users: 0,
    elite_users: 0,
    total_watermarks: 0,
    watermarks_today: 0
  });
  const [users, setUsers] = useState([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedUser, setSelectedUser] = useState(null);
  const [grantModalOpen, setGrantModalOpen] = useState(false);
  const [grantForm, setGrantForm] = useState({
    email: "",
    tier: "pro",
    duration_days: 30,
    reason: ""
  });

  // Check if user is admin
  useEffect(() => {
    if (!isAdmin()) {
      toast.error("Access denied. Admin privileges required.");
      navigate("/dashboard");
    } else {
      fetchAdminData();
    }
  }, []);

  const fetchAdminData = async () => {
    setLoading(true);
    try {
      // Fetch stats
      const statsResponse = await api.get("/admin/stats", {
        headers: { Authorization: `Bearer ${token}` }
      });
      setStats(statsResponse.data);

      // Fetch users
      const usersResponse = await api.get("/admin/users?limit=50", {
        headers: { Authorization: `Bearer ${token}` }
      });
      setUsers(usersResponse.data);
    } catch (error) {
      if (error.response?.status === 403) {
        toast.error("Admin access denied");
        navigate("/dashboard");
      } else {
        toast.error("Failed to load admin data");
      }
    } finally {
      setLoading(false);
    }
  };

  const handleGrantSubscription = async (e) => {
    e.preventDefault();
    try {
      await api.post("/admin/grant-subscription", grantForm, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      toast.success(`Granted ${grantForm.tier} to ${grantForm.email}`);
      setGrantModalOpen(false);
      setGrantForm({
        email: "",
        tier: "pro",
        duration_days: 30,
        reason: ""
      });
      
      // Refresh data
      fetchAdminData();
    } catch (error) {
      toast.error(error.response?.data?.detail || "Failed to grant subscription");
    }
  };

  const filteredUsers = users.filter(user => 
    user.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
    user.username.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const tabs = [
    { id: "overview", label: "Overview", icon: TrendingUp },
    { id: "users", label: "Users", icon: Users },
    { id: "subscriptions", label: "Subscriptions", icon: CreditCard }
  ];

  if (loading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-64">
          <Loader className="w-8 h-8 animate-spin text-primary-600" />
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="max-w-7xl mx-auto">
        {/* Admin Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <Shield className="w-8 h-8 text-primary-600" />
            Admin Panel
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">
            Manage users, subscriptions, and monitor system activity
          </p>
        </div>

        {/* Tabs */}
        <div className="flex space-x-1 mb-8 border-b border-gray-200 dark:border-gray-700">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`
                  flex items-center gap-2 px-4 py-3 font-medium transition-colors
                  border-b-2 -mb-[2px]
                  ${activeTab === tab.id
                    ? "border-primary-600 text-primary-600"
                    : "border-transparent text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-gray-100"
                  }
                `}
              >
                <Icon className="w-5 h-5" />
                {tab.label}
              </button>
            );
          })}
        </div>

        {/* Tab Content */}
        <motion.div
          key={activeTab}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
        >
          {/* Overview Tab */}
          {activeTab === "overview" && (
            <div className="space-y-8">
              {/* Stats Grid */}
              <div className="grid md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
                <StatsCard
                  title="Total Users"
                  value={stats.total_users}
                  icon={Users}
                  color="blue"
                />
                <StatsCard
                  title="Free Users"
                  value={stats.free_users}
                  icon={Users}
                  color="gray"
                />
                <StatsCard
                  title="Pro Users"
                  value={stats.pro_users}
                  icon={CreditCard}
                  color="purple"
                />
                <StatsCard
                  title="Elite Users"
                  value={stats.elite_users}
                  icon={Shield}
                  color="yellow"
                />
                <StatsCard
                  title="Total Watermarks"
                  value={stats.total_watermarks}
                  icon={Image}
                  color="green"
                />
                <StatsCard
                  title="Today's Watermarks"
                  value={stats.watermarks_today}
                  icon={Calendar}
                  color="pink"
                />
              </div>

              {/* Quick Actions */}
              <div className="card p-6">
                <h2 className="text-xl font-semibold mb-4">Quick Actions</h2>
                <div className="grid md:grid-cols-2 gap-4">
                  <button
                    onClick={() => setGrantModalOpen(true)}
                    className="flex items-center gap-3 p-4 bg-primary-50 dark:bg-primary-900/20 rounded-lg hover:bg-primary-100 dark:hover:bg-primary-900/30 transition-colors"
                  >
                    <Gift className="w-6 h-6 text-primary-600" />
                    <div className="text-left">
                      <h3 className="font-semibold text-primary-600 dark:text-primary-400">
                        Grant Subscription
                      </h3>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        Give free Pro/Elite access to users
                      </p>
                    </div>
                  </button>

                  <button
                    onClick={() => setActiveTab("users")}
                    className="flex items-center gap-3 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                  >
                    <Users className="w-6 h-6 text-gray-600 dark:text-gray-400" />
                    <div className="text-left">
                      <h3 className="font-semibold">Manage Users</h3>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        View and manage user accounts
                      </p>
                    </div>
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Users Tab */}
          {activeTab === "users" && (
            <div className="card p-6">
              {/* Search Bar */}
              <div className="mb-6">
                <div className="relative max-w-md">
                  <Search className="absolute left-3 top-3 w-5 h-5 text-gray-400" />
                  <input
                    type="text"
                    placeholder="Search users by email or username..."
                    className="input-field pl-10 w-full"
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                  />
                </div>
              </div>

              {/* Users Table */}
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-gray-200 dark:border-gray-700">
                      <th className="text-left py-3 px-4">User</th>
                      <th className="text-left py-3 px-4">Subscription</th>
                      <th className="text-left py-3 px-4">Watermarks</th>
                      <th className="text-left py-3 px-4">Joined</th>
                      <th className="text-left py-3 px-4">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredUsers.map((user) => (
                      <tr 
                        key={user.id}
                        className="border-b border-gray-100 dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-gray-800"
                      >
                        <td className="py-4 px-4">
                          <div>
                            <p className="font-medium">{user.username}</p>
                            <p className="text-sm text-gray-500">{user.email}</p>
                          </div>
                        </td>
                        <td className="py-4 px-4">
                          <span className={`
                            inline-flex px-2 py-1 text-xs font-medium rounded-full
                            ${user.subscription_tier === 'elite' ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-400' :
                              user.subscription_tier === 'pro' ? 'bg-purple-100 text-purple-800 dark:bg-purple-900/20 dark:text-purple-400' :
                              'bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-400'}
                          `}>
                            {user.subscription_tier.toUpperCase()}
                          </span>
                        </td>
                        <td className="py-4 px-4 text-sm">
                          {user.watermarks_count || 0}
                        </td>
                        <td className="py-4 px-4 text-sm text-gray-500">
                          {new Date(user.created_at).toLocaleDateString()}
                        </td>
                        <td className="py-4 px-4">
                          <button
                            onClick={() => {
                              setGrantForm({
                                ...grantForm,
                                email: user.email
                              });
                              setGrantModalOpen(true);
                            }}
                            className="text-primary-600 hover:text-primary-700 text-sm font-medium"
                          >
                            Grant Access
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Subscriptions Tab */}
          {activeTab === "subscriptions" && (
            <div className="card p-6">
              <div className="text-center py-12">
                <CreditCard className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-500 dark:text-gray-400">
                  Subscription analytics coming soon
                </p>
              </div>
            </div>
          )}
        </motion.div>

        {/* Grant Subscription Modal */}
        {grantModalOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50"
            onClick={() => setGrantModalOpen(false)}
          >
            <motion.div
              initial={{ scale: 0.9 }}
              animate={{ scale: 1 }}
              className="card p-6 max-w-md w-full"
              onClick={(e) => e.stopPropagation()}
            >
              <h2 className="text-xl font-semibold mb-4">Grant Subscription</h2>
              
              <form onSubmit={handleGrantSubscription} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-2">
                    User Email
                  </label>
                  <input
                    type="email"
                    required
                    className="input-field w-full"
                    value={grantForm.email}
                    onChange={(e) => setGrantForm({...grantForm, email: e.target.value})}
                    placeholder="user@example.com"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">
                    Subscription Tier
                  </label>
                  <select
                    className="input-field w-full"
                    value={grantForm.tier}
                    onChange={(e) => setGrantForm({...grantForm, tier: e.target.value})}
                  >
                    <option value="pro">Pro</option>
                    <option value="elite">Elite</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">
                    Duration (days)
                  </label>
                  <input
                    type="number"
                    min="1"
                    max="365"
                    required
                    className="input-field w-full"
                    value={grantForm.duration_days}
                    onChange={(e) => setGrantForm({...grantForm, duration_days: parseInt(e.target.value)})}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">
                    Reason
                  </label>
                  <textarea
                    className="input-field w-full"
                    rows="3"
                    value={grantForm.reason}
                    onChange={(e) => setGrantForm({...grantForm, reason: e.target.value})}
                    placeholder="Marketing campaign, partnership, etc."
                  />
                </div>

                <div className="flex gap-3 pt-4">
                  <button
                    type="submit"
                    className="btn-primary flex-1"
                  >
                    Grant Access
                  </button>
                  <button
                    type="button"
                    onClick={() => setGrantModalOpen(false)}
                    className="btn-secondary flex-1"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </motion.div>
          </motion.div>
        )}
      </div>
    </DashboardLayout>
  );
}

// Stats Card Component
function StatsCard({ title, value, icon: Icon, color }) {
  const colors = {
    blue: "bg-blue-100 text-blue-600 dark:bg-blue-900/20 dark:text-blue-400",
    gray: "bg-gray-100 text-gray-600 dark:bg-gray-900/20 dark:text-gray-400",
    purple: "bg-purple-100 text-purple-600 dark:bg-purple-900/20 dark:text-purple-400",
    yellow: "bg-yellow-100 text-yellow-600 dark:bg-yellow-900/20 dark:text-yellow-400",
    green: "bg-green-100 text-green-600 dark:bg-green-900/20 dark:text-green-400",
    pink: "bg-pink-100 text-pink-600 dark:bg-pink-900/20 dark:text-pink-400"
  };

  return (
    <div className="card p-4">
      <div className={`w-10 h-10 rounded-lg flex items-center justify-center mb-3 ${colors[color]}`}>
        <Icon className="w-5 h-5" />
      </div>
      <p className="text-2xl font-bold">{value.toLocaleString()}</p>
      <p className="text-sm text-gray-600 dark:text-gray-400">{title}</p>
    </div>
  );
}