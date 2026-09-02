import { createContext, useCallback, useEffect, useState } from "react";
import { isTokenExpired, parseJwt } from "../utils/jwt";

const AuthContext = createContext(null);

function readStoredUser() {
  try {
    const storedUser = localStorage.getItem("user");
    return storedUser ? JSON.parse(storedUser) : null;
  } catch {
    localStorage.removeItem("user");
    return null;
  }
}

function readStoredToken() {
  const storedToken = localStorage.getItem("token");
  if (!storedToken) return null;
  if (isTokenExpired(storedToken)) {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    return null;
  }
  return storedToken;
}

export function AuthProvider({ children }) {
  const initialToken = readStoredToken();
  const [token, setToken] = useState(initialToken);
  const [user, setUserState] = useState(() =>
    initialToken ? readStoredUser() : null,
  );

  // Keeps localStorage in sync, same as `login` already does —
  // so a refresh after a profile edit doesn't revert to stale data
  const setUser = useCallback((userData) => {
    setUserState(userData);
    if (userData) {
      localStorage.setItem("user", JSON.stringify(userData));
    } else {
      localStorage.removeItem("user");
    }
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    setToken(null);
    setUserState(null);
  }, []);

  const login = useCallback(
    (userData, accessToken) => {
      if (!accessToken) {
        logout();
        return;
      }
      localStorage.setItem("token", accessToken);
      localStorage.setItem("user", JSON.stringify(userData));
      setToken(accessToken);
      setUserState(userData);
    },
    [logout],
  );

  const isAuthenticated = Boolean(token) && !isTokenExpired(token);

  useEffect(() => {
    if (!token) return;
    if (isTokenExpired(token)) {
      logout();
      return;
    }
    const payload = parseJwt(token);
    const expiresAt = payload?.exp ? payload.exp * 1000 : null;
    if (!expiresAt) return;

    const delay = expiresAt - Date.now();
    if (delay <= 0) {
      logout();
      return;
    }

    const timer = window.setTimeout(logout, delay);
    return () => window.clearTimeout(timer);
  }, [token, logout]);

  return (
    <AuthContext.Provider
      value={{ user, token, login, logout, isAuthenticated, setUser }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export default AuthContext;
