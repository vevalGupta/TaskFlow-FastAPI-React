import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { authApi } from '../api/client';

const Ctx = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    if (!localStorage.getItem('accessToken')) { setLoading(false); return; }
    try { const { data } = await authApi.me(); setUser(data.data.user); }
    catch { localStorage.clear(); }
    finally { setLoading(false); }
  }, []);

  useEffect(() => { load(); }, [load]);

  const login = async creds => {
    const { data } = await authApi.login(creds);
    localStorage.setItem('accessToken',  data.data.accessToken);
    localStorage.setItem('refreshToken', data.data.refreshToken);
    setUser(data.data.user); return data.data.user;
  };

  const register = async payload => { const { data } = await authApi.register(payload); return data; };

  const logout = async () => {
    try { await authApi.logout(); } catch {}
    localStorage.clear(); setUser(null);
  };

  return <Ctx.Provider value={{ user, loading, login, register, logout }}>{children}</Ctx.Provider>;
};

export const useAuth = () => useContext(Ctx);