import React, { createContext, useContext, useState, useEffect } from 'react';
import {
  TOKEN_STORAGE_KEY,
  USER_STORAGE_KEY,
  loginUser,
  signupUser,
  fetchCurrentUser
} from '../services/api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => {
    try {
      return localStorage.getItem(TOKEN_STORAGE_KEY) || null;
    } catch {
      return null;
    }
  });

  const [user, setUser] = useState(() => {
    try {
      const stored = localStorage.getItem(USER_STORAGE_KEY);
      return stored ? JSON.parse(stored) : null;
    } catch {
      return null;
    }
  });

  const [isLoading, setIsLoading] = useState(true);
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false);
  const [authModalMode, setAuthModalMode] = useState('login'); // 'login' | 'signup'

  // Validate active token on initial mount
  useEffect(() => {
    async function verifySession() {
      if (!token) {
        setIsLoading(false);
        return;
      }

      try {
        const currentUser = await fetchCurrentUser(token);
        setUser(currentUser);
        localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(currentUser));
      } catch (err) {
        console.warn('[AuthContext] Session expired or invalid, reverting to guest mode:', err.message);
        setToken(null);
        setUser(null);
        localStorage.removeItem(TOKEN_STORAGE_KEY);
        localStorage.removeItem(USER_STORAGE_KEY);
      } finally {
        setIsLoading(false);
      }
    }

    verifySession();
  }, [token]);

  const openAuthModal = (mode = 'login') => {
    setAuthModalMode(mode);
    setIsAuthModalOpen(true);
  };

  const closeAuthModal = () => {
    setIsAuthModalOpen(false);
  };

  const login = async (email, password) => {
    const data = await loginUser(email, password);
    setToken(data.access_token);
    setUser(data.user);
    try {
      localStorage.setItem(TOKEN_STORAGE_KEY, data.access_token);
      localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(data.user));
    } catch (err) {
      console.error('[AuthContext] Failed to persist auth to localStorage:', err);
    }
    setIsAuthModalOpen(false);
    return data;
  };

  const signup = async (email, password, name) => {
    const data = await signupUser(email, password, name);
    setToken(data.access_token);
    setUser(data.user);
    try {
      localStorage.setItem(TOKEN_STORAGE_KEY, data.access_token);
      localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(data.user));
    } catch (err) {
      console.error('[AuthContext] Failed to persist auth to localStorage:', err);
    }
    setIsAuthModalOpen(false);
    return data;
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    try {
      localStorage.removeItem(TOKEN_STORAGE_KEY);
      localStorage.removeItem(USER_STORAGE_KEY);
    } catch (err) {
      console.error('[AuthContext] Failed to clear storage on logout:', err);
    }
  };

  const value = {
    user,
    token,
    isAuthenticated: Boolean(user && token),
    isLoading,
    isAuthModalOpen,
    authModalMode,
    openAuthModal,
    closeAuthModal,
    login,
    signup,
    logout
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

export default AuthContext;
