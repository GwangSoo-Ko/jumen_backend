import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const OAuth2Callback = () => {
  const navigate = useNavigate();
  const { setUser } = useAuth();

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const code = params.get('code');
    if (code) {
      fetch(`http://localhost:8000/auth/google/callback?code=${code}`)
        .then(res => {
          if (!res.ok) throw new Error('구글 인증 실패');
          return res.json();
        })
        .then(user => {
          console.log(user);
          setUser(user); // 로그인 상태 갱신
          navigate('/overview');
        })
        .catch(() => {
          alert('구글 로그인 실패');
          navigate('/sign-in');
        });
    } else {
      alert('구글 인증 코드 없음');
      navigate('/sign-in');
    }
  }, [navigate, setUser]);

  return <div>구글 로그인 처리 중...</div>;
};

export default OAuth2Callback; 