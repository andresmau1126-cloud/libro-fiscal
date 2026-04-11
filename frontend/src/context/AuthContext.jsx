import { createContext, useContext, useState, useEffect } from 'react';
import { authMe, authLogin, authRegister, authLogout } from '../services/api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    authMe()
      .then((data) => setUser(data.user))
      .catch(() => setUser(null))
      .finally(() => setLoading(false));
  }, []);

  const login = async (email, password) => {
    const data = await authLogin({ email, password });
    setUser(data.user);
    return data;
  };

  const register = async (nombre, email, password) => {
    const data = await authRegister({ nombre, email, password });
    setUser(data.user);
    return data;
  };

  const logout = async () => {
    await authLogout();
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
