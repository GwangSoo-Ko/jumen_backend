import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { alpha } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import Box from '@mui/material/Box';
import Stack from '@mui/material/Stack';
import AppNavbar from '../components/AppNavbar';
import Header from '../components/Header';
import SideMenu from '../components/SideMenu';
import AppTheme from '../shared-theme/AppTheme';
import {
  chartsCustomizations,
  dataGridCustomizations,
  datePickersCustomizations,
  treeViewCustomizations,
} from '../theme/customizations';
import { useAuth } from '../contexts/AuthContext';
import { useEffect } from 'react';

const xThemeComponents = {
  ...chartsCustomizations,
  ...dataGridCustomizations,
  ...datePickersCustomizations,
  ...treeViewCustomizations,
};

const samplePosts = [
  { id: 1, title: '자유롭게 소통해요', author: 'userA', createdAt: '2024-06-01', content: '여기는 자유롭게 소통하는 공간입니다.' },
  { id: 2, title: '오늘의 주식 이야기', author: 'userB', createdAt: '2024-06-02', content: '오늘 주식 시장에 대해 이야기해봐요.' },
  { id: 3, title: '잡담 환영합니다', author: 'userC', createdAt: '2024-06-03', content: '잡담도 언제나 환영입니다!' },
];

export default function FreeBoardDetail(props) {
  const { id } = useParams();
  const { user } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (!user) {
      alert('로그인 후 상세 내용을 볼 수 있습니다.');
      navigate('/sign-in');
    }
  }, [user, navigate]);

  const post = samplePosts.find((p) => String(p.id) === String(id));

  if (!post) {
    return <div style={{ padding: '2rem' }}><h2>글을 찾을 수 없습니다.</h2></div>;
  }

  return (
    <AppTheme {...props} themeComponents={xThemeComponents}>
      <CssBaseline enableColorScheme />
      <Box sx={{ display: 'flex' }}>
        <SideMenu />
        <AppNavbar />
        <Box
          component="main"
          sx={(theme) => ({
            flexGrow: 1,
            backgroundColor: theme.vars
              ? `rgba(${theme.vars.palette.background.defaultChannel} / 1)`
              : alpha(theme.palette.background.default, 1),
            overflow: 'auto',
          })}
        >
          <Stack
            spacing={2}
            sx={{
              alignItems: 'center',
              mx: 3,
              pb: 5,
              mt: { xs: 8, md: 0 },
            }}
          >
            <Header />
            <div style={{ padding: '2rem', maxWidth: 800, margin: '0 auto' }}>
              <h1>{post.title}</h1>
              <div style={{ color: '#888', marginBottom: 8 }}>
                작성자: {post.author} | 작성일: {post.createdAt}
              </div>
              <hr />
              <div style={{ marginTop: 24, fontSize: '1.1rem' }}>{post.content}</div>
            </div>
          </Stack>
        </Box>
      </Box>
    </AppTheme>
  );
} 