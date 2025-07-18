import React, { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext();

export async function fetchWithAuth(url, options = {}) {
  let token = localStorage.getItem('access_token');
  let res = await fetch(url, {
    ...options,
    credentials: 'include', // 쿠키 포함
    headers: { ...options.headers, Authorization: `Bearer ${token}` }
  });
  if (res.status === 401) {
    // access_token 만료 → refresh 시도
    const refreshRes = await fetch('http://localhost:8000/auth/refresh', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include', // 쿠키에서 refresh_token 자동 전송
    });
    if (refreshRes.ok) {
      const data = await refreshRes.json();
      localStorage.setItem('access_token', data.access_token);
      // refresh_token은 쿠키에서 관리되므로 localStorage에 저장하지 않음
      // 재시도
      res = await fetch(url, {
        ...options,
        credentials: 'include',
        headers: { ...options.headers, Authorization: `Bearer ${data.access_token}` }
      });
    } else {
      // 강제 로그아웃
      localStorage.removeItem('access_token');
      localStorage.removeItem('user_info');
      localStorage.removeItem('refresh_token'); // 혹시 남아있을 수 있는 refresh_token 제거
      window.location.href = '/sign-in';
      return;
    }
  }
  return res;
}

// 사용자 정보 가져오기 (토큰 검증 포함)
async function fetchUserInfo() {
  const token = localStorage.getItem('access_token');
  if (!token) {
    return null;
  }

  try {
    const response = await fetchWithAuth('http://localhost:8000/auth/me');
    if (response && response.ok) {
      const user = await response.json();
      localStorage.setItem('user_info', JSON.stringify(user));
      return user;
    }
  } catch (error) {
    console.error('사용자 정보 조회 실패:', error);
  }
  
  // 토큰이 유효하지 않으면 제거
  localStorage.removeItem('access_token');
  localStorage.removeItem('user_info');
  localStorage.removeItem('refresh_token'); // 혹시 남아있을 수 있는 refresh_token 제거
  return null;
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // 초기 로드 시 사용자 정보 확인
  useEffect(() => {
    const initializeAuth = async () => {
      setLoading(true);
      
      // 기존에 저장된 refresh_token이 있다면 제거 (보안상 문제)
      if (localStorage.getItem('refresh_token')) {
        console.warn('기존 refresh_token을 localStorage에서 제거합니다. (보안상 이유)');
        localStorage.removeItem('refresh_token');
      }
      
      // localStorage에서 사용자 정보 확인
      const savedUser = localStorage.getItem('user_info');
      if (savedUser) {
        try {
          const userData = JSON.parse(savedUser);
          setUser(userData);
        } catch (error) {
          console.error('저장된 사용자 정보 파싱 실패:', error);
          localStorage.removeItem('user_info');
        }
      }

      // 토큰이 있으면 서버에서 사용자 정보 검증
      const token = localStorage.getItem('access_token');
      if (token) {
        const userInfo = await fetchUserInfo();
        setUser(userInfo);
      }
      
      setLoading(false);
    };

    initializeAuth();
  }, []);

  // 로그아웃 함수
  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_info');
    localStorage.removeItem('refresh_token'); // 혹시 남아있을 수 있는 refresh_token 제거
    setUser(null);
    window.location.href = '/sign-in';
  };

  return (
    <AuthContext.Provider value={{ user, setUser, loading, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
} 