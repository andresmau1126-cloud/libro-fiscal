import { createContext, useContext, useState, useEffect } from 'react';
import { authMe, authLogin, authRegister, authVerifyRegistrationCode, authResendRegistrationCode, authLogout, authRequestOtp, authVerifyOtp } from '../services/api';

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

  const requestOtp = async (email, password) => {
    return await authRequestOtp({ email, password });
  };

  const verifyOtp = async (email, codigo) => {
    const data = await authVerifyOtp({ email, codigo });
    setUser(data.user);
    return data;
  };

  const register = async (nombre, email, password) => {
    return await authRegister({ nombre, email, password });
  };

  const verifyRegistrationCode = async (email, code) => {
    const data = await authVerifyRegistrationCode({ email, code });
    setUser(data.user);
    return data;
  };

  const resendRegistrationCode = async (email) => {
    return await authResendRegistrationCode({ email });
  };

  const logout = async () => {
    await authLogout();
    setUser(null);
  };

  const updateUser = (nextUser) => {
    setUser(nextUser);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, requestOtp, verifyOtp, register, verifyRegistrationCode, resendRegistrationCode, logout, updateUser }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
