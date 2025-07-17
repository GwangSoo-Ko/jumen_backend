import React, { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext();

export async function fetchWithAuth(url, options = {}) {
  let token = localStorage.getItem('access_token');
  let res = await fetch(url, {
    ...options,
    headers: { ...options.headers, Authorization: `Bearer ${token}` }
  });
  if (res.status === 401) {
    // access_token 만료 → refresh 시도
    const refreshToken = localStorage.getItem('refresh_token');
    const refreshRes = await fetch('http://localhost:8000/auth/refresh', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: refreshToken })
    });
    if (refreshRes.ok) {
      const data = await refreshRes.json();
      localStorage.setItem('access_token', data.access_token);
      localStorage.setItem('refresh_token', data.refresh_token);
      // 재시도
      res = await fetch(url, {
        ...options,
        headers: { ...options.headers, Authorization: `Bearer ${data.access_token}` }
      });
    } else {
      // 강제 로그아웃
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      window.location.href = '/sign-in';
      return;
    }
  }
  return res;
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) {
      fetch('http://localhost:8000/auth/me', {
        headers: { Authorization: `Bearer ${token}` }
      })
        .then(res => {
          if (!res.ok) throw new Error('토큰 만료 또는 인증 실패');
          return res.json();
        })
        .then(user => setUser(user))
        .catch(() => setUser(null));
    }
  }, []);

  return (
    <AuthContext.Provider value={{ user, setUser }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
} 