import React from 'react';
import { Link } from 'react-router-dom';
import { BeakerIcon, UserCircleIcon } from '@heroicons/react/24/outline';
import { AuthState } from '../types';

interface HeaderProps {
  authState: AuthState;
  onLogout: () => void;
}

const Header: React.FC<HeaderProps> = ({ authState, onLogout }) => {
  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="container mx-auto px-4">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center">
            <Link to="/" className="flex items-center space-x-2">
              <BeakerIcon className="h-8 w-8 text-primary-600" />
              <span className="text-xl font-bold text-gray-900">
                SoA Optimizer
              </span>
            </Link>
            
            <nav className="ml-10 hidden md:flex space-x-8">
              <Link
                to="/"
                className="text-gray-600 hover:text-gray-900 px-3 py-2 text-sm font-medium"
              >
                Dashboard
              </Link>
              <Link
                to="/upload"
                className="text-gray-600 hover:text-gray-900 px-3 py-2 text-sm font-medium"
              >
                Upload Schedule
              </Link>
              {authState.isAuthenticated && (
                <Link
                  to="/results"
                  className="text-gray-600 hover:text-gray-900 px-3 py-2 text-sm font-medium"
                >
                  My Results
                </Link>
              )}
              <Link
                to="/about"
                className="text-gray-600 hover:text-gray-900 px-3 py-2 text-sm font-medium"
              >
                About
              </Link>
            </nav>
          </div>
          
          <div className="flex items-center space-x-4">
            {authState.isAuthenticated ? (
              <>
                <div className="flex items-center space-x-2">
                  <UserCircleIcon className="h-6 w-6 text-gray-400" />
                  <span className="text-sm text-gray-700">
                    {authState.user?.full_name}
                  </span>
                </div>
                <button
                  onClick={onLogout}
                  className="text-sm text-gray-600 hover:text-gray-900"
                >
                  Logout
                </button>
              </>
            ) : (
              <>
                <Link
                  to="/login"
                  className="text-sm text-gray-600 hover:text-gray-900"
                >
                  Login
                </Link>
                <Link
                  to="/register"
                  className="bg-primary-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-primary-700"
                >
                  Sign Up
                </Link>
              </>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;