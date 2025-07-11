// frontend/src/services/api.js

import axios from 'axios'

// WICHTIG: Stelle sicher, dass die URL korrekt ist
const API_URL = import.meta.env.VITE_API_URL || 'https://watermark-backend-a4l8.onrender.com'

console.log('API URL:', API_URL) // Debug log

const api = axios.create({
  baseURL: `${API_URL}/api`,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Log every request for debugging
    console.log('Making request to:', config.url)
    console.log('Request method:', config.method)
    console.log('Request data:', config.data)
    
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    console.error('Request error:', error)
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  (response) => {
    console.log('Response received:', response.data)
    return response
  },
  (error) => {
    console.error('Response error:', error)
    
    if (error.response) {
      // Server responded with error
      console.error('Error response:', error.response.data)
      console.error('Error status:', error.response.status)
      
      if (error.response.status === 401) {
        localStorage.removeItem('token')
        localStorage.removeItem('auth-storage')
        
        if (!window.location.pathname.includes('/login')) {
          window.location.href = '/login'
        }
      }
    } else if (error.request) {
      // Request made but no response
      console.error('No response received:', error.request)
    } else {
      // Something else happened
      console.error('Error setting up request:', error.message)
    }
    
    return Promise.reject(error)
  }
)

export default api