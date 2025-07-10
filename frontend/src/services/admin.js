// File: frontend/src/services/admin.js

import api from "./api";

export const adminService = {
  // Get admin statistics
  getStats: async () => {
    const response = await api.get("/admin/stats");
    return response.data;
  },

  // Get all users with pagination
  getUsers: async (skip = 0, limit = 50) => {
    const response = await api.get("/admin/users", {
      params: { skip, limit }
    });
    return response.data;
  },

  // Grant subscription to user
  grantSubscription: async (data) => {
    const response = await api.post("/admin/grant-subscription", data);
    return response.data;
  },

  // Search users
  searchUsers: async (query) => {
    const response = await api.get("/admin/users/search", {
      params: { q: query }
    });
    return response.data;
  },

  // Get user details
  getUserDetails: async (userId) => {
    const response = await api.get(`/admin/users/${userId}`);
    return response.data;
  },

  // Update user subscription
  updateUserSubscription: async (userId, data) => {
    const response = await api.put(`/admin/users/${userId}/subscription`, data);
    return response.data;
  },

  // Get admin activity logs
  getActivityLogs: async (skip = 0, limit = 50) => {
    const response = await api.get("/admin/logs", {
      params: { skip, limit }
    });
    return response.data;
  }
};