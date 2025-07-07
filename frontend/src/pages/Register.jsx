import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { Mail, Lock, User, Loader } from "lucide-react";
import toast from "react-hot-toast";
import Header from "../components/common/Header";
import { useAuthStore } from "../hooks/useAuth";

export default function Register() {
  const navigate = useNavigate();
  const { register, isLoading } = useAuthStore();
  const [formData, setFormData] = useState({
    email: "",
    username: "",
    password: "",
    confirmPassword: "",
  });

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (formData.password !== formData.confirmPassword) {
      toast.error("Passwords do not match");
      return;
    }

    if (formData.password.length < 8) {
      toast.error("Password must be at least 8 characters");
      return;
    }

    const result = await register({
      email: formData.email,
      username: formData.username,
      password: formData.password,
    });

    if (result.success) {
      toast.success("Account created successfully!");
      navigate("/dashboard");
    } else {
      toast.error(result.error);
    }
  };

  const handleGoogleSignup = () => {
    window.location.href = `${import.meta.env.VITE_API_URL}/api/auth/google`;
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-dark-bg">
      <Header />

      <div className="container mx-auto px-4 py-16">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="max-w-md mx-auto"
        >
          <div className="card p-8">
            <h2 className="text-3xl font-bold text-center mb-8">
              Create Account
            </h2>

            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <label className="block text-sm font-medium mb-2">Email</label>
                <div className="relative">
                  <Mail className="absolute left-3 top-3 w-5 h-5 text-gray-400" />
                  <input
                    type="email"
                    required
                    className="input-field pl-10"
                    placeholder="you@example.com"
                    value={formData.email}
                    onChange={(e) =>
                      setFormData({ ...formData, email: e.target.value })
                    }
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">
                  Username
                </label>
                <div className="relative">
                  <User className="absolute left-3 top-3 w-5 h-5 text-gray-400" />
                  <input
                    type="text"
                    required
                    className="input-field pl-10"
                    placeholder="johndoe"
                    value={formData.username}
                    onChange={(e) =>
                      setFormData({ ...formData, username: e.target.value })
                    }
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">
                  Password
                </label>
                <div className="relative">
                  <Lock className="absolute left-3 top-3 w-5 h-5 text-gray-400" />
                  <input
                    type="password"
                    required
                    className="input-field pl-10"
                    placeholder="••••••••"
                    value={formData.password}
                    onChange={(e) =>
                      setFormData({ ...formData, password: e.target.value })
                    }
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">
                  Confirm Password
                </label>
                <div className="relative">
                  <Lock className="absolute left-3 top-3 w-5 h-5 text-gray-400" />
                  <input
                    type="password"
                    required
                    className="input-field pl-10"
                    placeholder="••••••••"
                    value={formData.confirmPassword}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        confirmPassword: e.target.value,
                      })
                    }
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={isLoading}
                className="w-full btn-primary py-3 flex items-center justify-center"
              >
                {isLoading ? (
                  <Loader className="w-5 h-5 animate-spin" />
                ) : (
                  "Create Account"
                )}
              </button>
            </form>

            <div className="relative my-6">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-300 dark:border-dark-border"></div>
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-2 bg-white dark:bg-dark-surface text-gray-500">
                  Or continue with
                </span>
              </div>
            </div>

            <button
              onClick={handleGoogleSignup}
              className="w-full btn-secondary py-3 flex items-center justify-center space-x-2"
            >
              <svg className="w-5 h-5" viewBox="0 0 24 24">
                <path
                  fill="#4285F4"
                  d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                />
                <path
                  fill="#34A853"
                  d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                />
                <path
                  fill="#FBBC05"
                  d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                />
                <path
                  fill="#EA4335"
                  d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                />
              </svg>
              <span>Sign up with Google</span>
            </button>

            <p className="text-center mt-6 text-sm text-gray-600 dark:text-gray-400">
              Already have an account?{" "}
              <Link
                to="/login"
                className="text-primary-600 hover:text-primary-700 font-medium"
              >
                Sign in
              </Link>
            </p>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
