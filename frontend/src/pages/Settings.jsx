import { useState } from "react";
import { motion } from "framer-motion";
import { User, Mail, Key, Bell, CreditCard, Save, Loader } from "lucide-react";
import DashboardLayout from "../components/dashboard/DashboardLayout";
import { useAuthStore } from "../hooks/useAuth";
import toast from "react-hot-toast";
import api from "../services/api";

export default function Settings() {
  const { user, token } = useAuthStore();
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState("profile");

  const [profileData, setProfileData] = useState({
    username: user?.username || "",
    email: user?.email || "",
  });

  const [passwordData, setPasswordData] = useState({
    currentPassword: "",
    newPassword: "",
    confirmPassword: "",
  });

  const handleProfileUpdate = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      await api.put("/users/me", profileData, {
        headers: { Authorization: `Bearer ${token}` },
      });
      toast.success("Profile updated successfully");
    } catch (error) {
      toast.error(error.response?.data?.detail || "Failed to update profile");
    } finally {
      setLoading(false);
    }
  };

  const handlePasswordUpdate = async (e) => {
    e.preventDefault();

    if (passwordData.newPassword !== passwordData.confirmPassword) {
      toast.error("New passwords do not match");
      return;
    }

    if (passwordData.newPassword.length < 8) {
      toast.error("Password must be at least 8 characters");
      return;
    }

    setLoading(true);

    try {
      await api.post(
        "/users/change-password",
        {
          current_password: passwordData.currentPassword,
          new_password: passwordData.newPassword,
        },
        {
          headers: { Authorization: `Bearer ${token}` },
        },
      );

      toast.success("Password updated successfully");
      setPasswordData({
        currentPassword: "",
        newPassword: "",
        confirmPassword: "",
      });
    } catch (error) {
      toast.error(error.response?.data?.detail || "Failed to update password");
    } finally {
      setLoading(false);
    }
  };

  const tabs = [
    { id: "profile", label: "Profile", icon: User },
    { id: "security", label: "Security", icon: Key },
    { id: "billing", label: "Billing", icon: CreditCard },
    { id: "notifications", label: "Notifications", icon: Bell },
  ];

  return (
    <DashboardLayout>
      <div className="max-w-4xl">
        <h1 className="text-3xl font-bold mb-8">Settings</h1>

        <div className="flex space-x-8">
          {/* Tabs */}
          <div className="w-48">
            <nav className="space-y-2">
              {tabs.map((tab) => {
                const Icon = tab.icon;
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`
                      w-full flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors
                      ${
                        activeTab === tab.id
                          ? "bg-primary-100 dark:bg-primary-900/20 text-primary-600 dark:text-primary-400"
                          : "hover:bg-gray-100 dark:hover:bg-dark-border"
                      }
                    `}
                  >
                    <Icon className="w-5 h-5" />
                    <span className="font-medium">{tab.label}</span>
                  </button>
                );
              })}
            </nav>
          </div>

          {/* Content */}
          <div className="flex-1">
            <motion.div
              key={activeTab}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              className="card p-6"
            >
              {/* Profile Tab */}
              {activeTab === "profile" && (
                <form onSubmit={handleProfileUpdate} className="space-y-6">
                  <h2 className="text-xl font-semibold mb-4">
                    Profile Information
                  </h2>

                  <div>
                    <label className="block text-sm font-medium mb-2">
                      Username
                    </label>
                    <input
                      type="text"
                      className="input-field"
                      value={profileData.username}
                      onChange={(e) =>
                        setProfileData({
                          ...profileData,
                          username: e.target.value,
                        })
                      }
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-2">
                      Email
                    </label>
                    <input
                      type="email"
                      className="input-field"
                      value={profileData.email}
                      disabled={user?.google_id} // Disable if Google auth
                      onChange={(e) =>
                        setProfileData({
                          ...profileData,
                          email: e.target.value,
                        })
                      }
                    />
                    {user?.google_id && (
                      <p className="text-sm text-gray-500 mt-1">
                        Email cannot be changed for Google accounts
                      </p>
                    )}
                  </div>

                  <button
                    type="submit"
                    disabled={loading}
                    className="btn-primary flex items-center space-x-2"
                  >
                    {loading ? (
                      <Loader className="w-5 h-5 animate-spin" />
                    ) : (
                      <>
                        <Save className="w-5 h-5" />
                        <span>Save Changes</span>
                      </>
                    )}
                  </button>
                </form>
              )}

              {/* Security Tab */}
              {activeTab === "security" && (
                <form onSubmit={handlePasswordUpdate} className="space-y-6">
                  <h2 className="text-xl font-semibold mb-4">
                    Change Password
                  </h2>

                  {user?.google_id ? (
                    <p className="text-gray-600 dark:text-gray-400">
                      Password management is not available for Google accounts.
                    </p>
                  ) : (
                    <>
                      <div>
                        <label className="block text-sm font-medium mb-2">
                          Current Password
                        </label>
                        <input
                          type="password"
                          className="input-field"
                          value={passwordData.currentPassword}
                          onChange={(e) =>
                            setPasswordData({
                              ...passwordData,
                              currentPassword: e.target.value,
                            })
                          }
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium mb-2">
                          New Password
                        </label>
                        <input
                          type="password"
                          className="input-field"
                          value={passwordData.newPassword}
                          onChange={(e) =>
                            setPasswordData({
                              ...passwordData,
                              newPassword: e.target.value,
                            })
                          }
                          minLength={8}
                          required
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium mb-2">
                          Confirm New Password
                        </label>
                        <input
                          type="password"
                          className="input-field"
                          value={passwordData.confirmPassword}
                          onChange={(e) =>
                            setPasswordData({
                              ...passwordData,
                              confirmPassword: e.target.value,
                            })
                          }
                          minLength={8}
                          required
                        />
                      </div>

                      <button
                        type="submit"
                        disabled={loading}
                        className="btn-primary flex items-center space-x-2"
                      >
                        {loading ? (
                          <Loader className="w-5 h-5 animate-spin" />
                        ) : (
                          "Update Password"
                        )}
                      </button>
                    </>
                  )}
                </form>
              )}

              {/* Billing Tab */}
              {activeTab === "billing" && (
                <div className="space-y-6">
                  <h2 className="text-xl font-semibold mb-4">
                    Billing & Subscription
                  </h2>

                  <div className="p-4 bg-gray-50 dark:bg-dark-bg rounded-lg">
                    <div className="flex justify-between items-center mb-2">
                      <span className="font-medium">Current Plan</span>
                      <span className="text-lg font-bold text-primary-600">
                        {user?.subscription_tier?.toUpperCase()}
                      </span>
                    </div>

                    {user?.subscription_end_date && (
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        Renews on{" "}
                        {new Date(
                          user.subscription_end_date,
                        ).toLocaleDateString()}
                      </p>
                    )}
                  </div>

                  {user?.subscription_tier !== "free" && (
                    <button className="btn-secondary w-full">
                      Manage Subscription
                    </button>
                  )}

                  {user?.subscription_tier === "free" && (
                    <a
                      href="/pricing"
                      className="btn-primary w-full text-center"
                    >
                      Upgrade Your Plan
                    </a>
                  )}
                </div>
              )}

              {/* Notifications Tab */}
              {activeTab === "notifications" && (
                <div className="space-y-6">
                  <h2 className="text-xl font-semibold mb-4">
                    Notification Preferences
                  </h2>

                  <div className="space-y-4">
                    <label className="flex items-center justify-between p-4 bg-gray-50 dark:bg-dark-bg rounded-lg">
                      <div>
                        <p className="font-medium">Email Notifications</p>
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                          Receive updates about your watermarks and account
                        </p>
                      </div>
                      <input
                        type="checkbox"
                        className="toggle"
                        defaultChecked
                      />
                    </label>

                    <label className="flex items-center justify-between p-4 bg-gray-50 dark:bg-dark-bg rounded-lg">
                      <div>
                        <p className="font-medium">Marketing Emails</p>
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                          New features and special offers
                        </p>
                      </div>
                      <input type="checkbox" className="toggle" />
                    </label>
                  </div>
                </div>
              )}
            </motion.div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
