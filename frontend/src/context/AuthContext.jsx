import { createContext, useContext, useEffect, useMemo, useState } from "react";

import { api } from "../api/client";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [permissions, setPermissions] = useState(null);
  const [loading, setLoading] = useState(Boolean(localStorage.getItem("eventops.access")));

  async function loadMe() {
    const [me, perms] = await Promise.all([
      api.get("/auth/me/"),
      api.get("/auth/permissions/"),
    ]);
    setUser(me.data);
    setPermissions(perms.data);
    return me.data;
  }

  useEffect(() => {
    if (!localStorage.getItem("eventops.access")) {
      setLoading(false);
      return;
    }
    loadMe().catch(() => setUser(null)).finally(() => setLoading(false));
  }, []);

  async function login(username, password) {
    const response = await api.post("/auth/login/", { username, password });
    localStorage.setItem("eventops.access", response.data.access);
    localStorage.setItem("eventops.refresh", response.data.refresh);
    return loadMe();
  }

  function logout() {
    localStorage.removeItem("eventops.access");
    localStorage.removeItem("eventops.refresh");
    setUser(null);
    setPermissions(null);
  }

  const value = useMemo(
    () => ({
      user,
      role: user?.role_code,
      permissions,
      loading,
      login,
      logout,
      isAuthenticated: Boolean(user),
      hasRole: (roles) => !roles || roles.includes(user?.role_code),
    }),
    [user, permissions, loading]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  return useContext(AuthContext);
}
