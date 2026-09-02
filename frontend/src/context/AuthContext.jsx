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
  const [user, setUser] = useState(() =>
    initialToken ? readStoredUser() : null,
  );

  const logout = useCallback(() => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    setToken(null);
    setUser(null);
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
      setUser(userData);
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
      value={{ user, token, login, logout, isAuthenticated }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export default AuthContext;
