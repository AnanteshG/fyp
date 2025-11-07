import { Outlet, Link, useLocation } from 'react-router-dom'
import { SignedIn, SignedOut, UserButton, useAuth } from '@clerk/clerk-react'
import { useEffect } from 'react'
import { setAuthToken } from '../api'

export default function Layout() {
  const location = useLocation()
  const { getToken } = useAuth()

  // Set auth token when user is authenticated
  useEffect(() => {
    const updateToken = async () => {
      try {
        const token = await getToken()
        setAuthToken(token)
      } catch (error) {
        console.error('Failed to get auth token:', error)
      }
    }
    updateToken()
  }, [getToken])

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex">
              <Link to="/" className="flex items-center">
                <span className="text-2xl font-bold text-blue-600">SlideX</span>
              </Link>
              <div className="hidden sm:ml-8 sm:flex sm:space-x-8">
                <Link
                  to="/"
                  className={`inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium ${location.pathname === '/'
                      ? 'border-blue-500 text-gray-900'
                      : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
                    }`}
                >
                  Home
                </Link>
                <Link
                  to="/generate"
                  className={`inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium ${location.pathname === '/generate'
                      ? 'border-blue-500 text-gray-900'
                      : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
                    }`}
                >
                  Generate
                </Link>
                <Link
                  to="/history"
                  className={`inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium ${location.pathname === '/history'
                      ? 'border-blue-500 text-gray-900'
                      : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
                    }`}
                >
                  History
                </Link>
              </div>
            </div>

            {/* Auth Section */}
            <div className="flex items-center">
              <SignedOut>
                <Link
                  to="/sign-in"
                  className="text-gray-700 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium"
                >
                  Sign In
                </Link>
                <Link
                  to="/sign-up"
                  className="ml-3 bg-blue-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-blue-700"
                >
                  Sign Up
                </Link>
              </SignedOut>
              <SignedIn>
                <UserButton afterSignOutUrl="/" />
              </SignedIn>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <Outlet />
      </main>

      <footer className="bg-white border-t border-gray-200 mt-12">
        <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
          <p className="text-center text-gray-500 text-sm">
            © 2025 SlideX. Powered by Claude, Groq & Pixabay.
          </p>
        </div>
      </footer>
    </div>
  )
}
