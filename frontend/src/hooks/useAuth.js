import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import api from '../services/api'

export const useAuthStore = create(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,

      login: async (email, password) => {
        set({ isLoading: true })
        try {
          const response = await api.post('/auth/login', {
            username: email, // OAuth2PasswordRequestForm expects username
            password
          })
          
          const { access_token } = response.data
          
          set({
            token: access_token,
            isAuthenticated: true,
            isLoading: false
          })
          
          // Get user data
          await get().fetchUser()
          
          return { success: true }
        } catch (error) {
          set({ isLoading: false })
          return { 
            success: false, 
            error: error.response?.data?.detail || 'Login failed' 
          }
        }
      },

      register: async (userData) => {
        set({ isLoading: true })
        try {
          await api.post('/auth/register', userData)
          
          // Auto login after registration
          return await get().login(userData.email, userData.password)
        } catch (error) {
          set({ isLoading: false })
          return { 
            success: false, 
            error: error.response?.data?.detail || 'Registration failed' 
          }
        }
      },

      logout: () => {
        set({
          user: null,
          token: null,
          isAuthenticated: false
        })
      },

      fetchUser: async () => {
        const token = get().token
        if (!token) return
        
        try {
          const response = await api.get('/users/me', {
            headers: { Authorization: `Bearer ${token}` }
          })
          
          set({ user: response.data })
        } catch (error) {
          // Token invalid, logout
          get().logout()
        }
      },

      checkAuth: () => {
        const token = get().token
        if (token) {
          get().fetchUser()
        }
      }
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({ token: state.token })
    }
  )
)
