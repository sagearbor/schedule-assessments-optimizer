import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

import Header from './components/Header';
import Dashboard from './components/Dashboard';
import ScheduleUpload from './components/ScheduleUpload';
import OptimizationResults from './components/OptimizationResults';
import Login from './components/Login';
import Register from './components/Register';
import About from './components/About';
import { AuthState } from './types';
import { authService } from './services/api';

function App() {
  const [authState, setAuthState] = useState<AuthState>({
    user: null,
    token: localStorage.getItem('token'),
    isAuthenticated: false,
  });

  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem('token');
      if (token) {
        try {
          const user = await authService.getCurrentUser();
          setAuthState({
            user,
            token,
            isAuthenticated: true,
          });
        } catch (error) {
          localStorage.removeItem('token');
          setAuthState({
            user: null,
            token: null,
            isAuthenticated: false,
          });
        }
      }
    };
    checkAuth();
  }, []);

  const handleLogin = (user: any, token: string) => {
    localStorage.setItem('token', token);
    setAuthState({
      user,
      token,
      isAuthenticated: true,
    });
  };

  const handleLogout = () => {
    authService.logout();
    setAuthState({
      user: null,
      token: null,
      isAuthenticated: false,
    });
  };

  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Header authState={authState} onLogout={handleLogout} />
        
        <main className="container mx-auto px-4 py-8">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/upload" element={<ScheduleUpload />} />
            <Route path="/results" element={<OptimizationResults />} />
            <Route path="/about" element={<About />} />
            <Route 
              path="/login" 
              element={
                authState.isAuthenticated ? 
                <Navigate to="/" /> : 
                <Login onLogin={handleLogin} />
              } 
            />
            <Route 
              path="/register" 
              element={
                authState.isAuthenticated ? 
                <Navigate to="/" /> : 
                <Register onRegister={handleLogin} />
              } 
            />
          </Routes>
        </main>
        
        <ToastContainer
          position="top-center"
          autoClose={5000}
          hideProgressBar={false}
          newestOnTop={false}
          closeOnClick
          rtl={false}
          pauseOnFocusLoss
          draggable
          pauseOnHover
        />
      </div>
    </Router>
  );
}

export default App;