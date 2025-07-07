import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Droplets, Menu, X, Sun, Moon } from 'lucide-react'
import { useState } from 'react'
import { useAuthStore } from '../../hooks/useAuth'
import { useTheme } from '../../hooks/useTheme'

export default function Header() {
  const [isMenuOpen, setIsMenuOpen] = useState(false)
  const { isAuthenticated } = useAuthStore()
  const { theme, toggleTheme } = useTheme()

  return (
    <header className="sticky top-0 z-50 bg-white/80 dark:bg-dark-surface/80 backdrop-blur-lg border-b border-gray-200 dark:border-dark-border">
      <nav className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-2">
            <motion.div
              whileHover={{ rotate: 360 }}
              transition={{ duration: 0.5 }}
            >
              <Droplets className="w-8 h-8 text-primary-600" />
            </motion.div>
            <span className="text-xl font-bold bg-gradient-to-r from-primary-600 to-primary-400 bg-clip-text text-transparent">
              AI Watermark
            </span>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-8">
            <Link to="/pricing" className="hover:text-primary-600 transition-colors">
              Pricing
            </Link>
            {isAuthenticated ? (
              <>
                <Link to="/dashboard" className="hover:text-primary-600 transition-colors">
                  Dashboard
                </Link>
                <Link to="/create" className="btn-primary">
                  Create Watermark
                </Link>
              </>
            ) : (
              <>
                <Link to="/login" className="hover:text-primary-600 transition-colors">
                  Login
                </Link>
                <Link to="/register" className="btn-primary">
                  Get Started
                </Link>
              </>
            )}
            
            {/* Theme Toggle */}
            <button
              onClick={toggleTheme}
              className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-dark-border transition-colors"
            >
              {theme === 'dark' ? (
                <Sun className="w-5 h-5" />
              ) : (
                <Moon className="w-5 h-5" />
              )}
            </button>
          </div>

          {/* Mobile Menu Button */}
          <button
            onClick={() => setIsMenuOpen(!isMenuOpen)}
            className="md:hidden p-2"
          >
            {isMenuOpen ? (
              <X className="w-6 h-6" />
            ) : (
              <Menu className="w-6 h-6" />
            )}
          </button>
        </div>

        {/* Mobile Navigation */}
        {isMenuOpen && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="md:hidden mt-4 pb-4 border-t border-gray-200 dark:border-dark-border pt-4"
          >
            <div className="flex flex-col space-y-4">
              <Link to="/pricing" className="hover:text-primary-600 transition-colors">
                Pricing
              </Link>
              {isAuthenticated ? (
                <>
                  <Link to="/dashboard" className="hover:text-primary-600 transition-colors">
                    Dashboard
                  </Link>
                  <Link to="/create" className="btn-primary text-center">
                    Create Watermark
                  </Link>
                </>
              ) : (
                <>
                  <Link to="/login" className="hover:text-primary-600 transition-colors">
                    Login
                  </Link>
                  <Link to="/register" className="btn-primary text-center">
                    Get Started
                  </Link>
                </>
              )}
            </div>
          </motion.div>
        )}
      </nav>
    </header>
  )
}
