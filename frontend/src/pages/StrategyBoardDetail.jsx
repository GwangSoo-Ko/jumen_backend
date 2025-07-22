import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { alpha } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import Box from '@mui/material/Box';
import Stack from '@mui/material/Stack';
import { Button, Typography, Divider, CircularProgress, Alert, Chip } from '@mui/material';
import { ThumbUp, ThumbDown, Comment, Visibility, Edit, Delete } from '@mui/icons-material';
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
import { useAuth, fetchWithAuth } from '../contexts/AuthContext';
import Copyright from '../internals/components/Copyright';

const xThemeComponents = {
  ...chartsCustomizations,
  ...dataGridCustomizations,
  ...datePickersCustomizations,
  ...treeViewCustomizations,
};

// HTML 태그를 안전하게 처리하는 유틸리티 함수 (XSS 방지)
const sanitizeHtml = (html) => {
  if (!html) return '';
  // 기본적인 XSS 방지 (실제 프로덕션에서는 DOMPurify 같은 라이브러리 사용 권장)
  return html.replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '');
};

export default function StrategyBoardDetail(props) {
  const { id } = useParams();
  const { user } = useAuth();
  const navigate = useNavigate();
  
  // 상태 관리
  const [strategy, setStrategy] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isLiked, setIsLiked] = useState(false);

  // 게시글 상세 조회
  const fetchStrategyDetail = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetchWithAuth(`http://localhost:8000/strategy-board/posts/${id}`);
      
      if (!response.ok) {
        if (response.status === 404) {
          throw new Error('게시글을 찾을 수 없습니다.');
        }
        throw new Error('게시글을 불러오는데 실패했습니다.');
      }

      const data = await response.json();
      setStrategy(data);
      setIsLiked(data.is_liked);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // 좋아요 토글
  const handleLikeToggle = async () => {
    if (!user) {
      alert('로그인 후 이용 가능합니다.');
      return;
    }

    try {
      const response = await fetchWithAuth(`http://localhost:8000/strategy-board/posts/${id}/like`, {
        method: 'POST'
      });
      
      if (!response.ok) {
        throw new Error('좋아요 처리에 실패했습니다.');
      }

      const data = await response.json();
      setIsLiked(data.is_liked);
      setStrategy(prev => ({
        ...prev,
        like_count: data.like_count
      }));
    } catch (err) {
      alert(err.message);
    }
  };

  // 게시글 삭제
  const handleDelete = async () => {
    if (!user || strategy.user_id !== user.id) {
      alert('삭제 권한이 없습니다.');
      return;
    }

    if (!confirm('정말로 이 게시글을 삭제하시겠습니까?')) {
      return;
    }

    try {
      const response = await fetchWithAuth(`http://localhost:8000/strategy-board/posts/${id}`, {
        method: 'DELETE'
      });
      
      if (!response.ok) {
        throw new Error('게시글 삭제에 실패했습니다.');
      }

      alert('게시글이 삭제되었습니다.');
      navigate('/strategy-board');
    } catch (err) {
      alert(err.message);
    }
  };

  useEffect(() => {
    fetchStrategyDetail();
  }, [id]);

  if (loading) {
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
              <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 400 }}>
                <CircularProgress />
              </Box>
            </Stack>
          </Box>
        </Box>
      </AppTheme>
    );
  }

  if (error) {
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
              <Alert severity="error" sx={{ maxWidth: 600 }}>
                {error}
              </Alert>
            </Stack>
          </Box>
        </Box>
      </AppTheme>
    );
  }

  if (!strategy) {
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
              <Alert severity="warning" sx={{ maxWidth: 600 }}>
                전략을 찾을 수 없습니다.
              </Alert>
            </Stack>
          </Box>
        </Box>
      </AppTheme>
    );
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
            <Box sx={{ maxWidth: 900, width: '100%', p: 3 }}>
              {/* 게시글 헤더 */}
              <Box sx={{ mb: 3 }}>
                <Typography variant="h4" component="h1" gutterBottom>
                  {strategy.title}
                </Typography>
                
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                  <Typography variant="body2" color="text.secondary">
                    작성자: {strategy.user_nickname}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    작성일: {new Date(strategy.crt_date).toLocaleDateString('ko-KR')}
                  </Typography>
                  {strategy.is_notice && (
                    <Chip label="공지" color="primary" size="small" />
                  )}
                </Box>

                <Box sx={{ display: 'flex', alignItems: 'center', gap: 3, mb: 2 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Visibility fontSize="small" />
                    <Typography variant="body2">{strategy.view_count}</Typography>
                  </Box>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <ThumbUp fontSize="small" />
                    <Typography variant="body2">{strategy.like_count}</Typography>
                  </Box>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Comment fontSize="small" />
                    <Typography variant="body2">{strategy.comment_count}</Typography>
                  </Box>
                </Box>

                {/* 작성자만 수정/삭제 버튼 표시 */}
                {user && strategy.user_id === user.id && (
                  <Box sx={{ display: 'flex', gap: 1 }}>
                    <Button
                      variant="outlined"
                      size="small"
                      startIcon={<Edit />}
                      onClick={() => navigate(`/strategy-board/edit/${id}`)}
                    >
                      수정
                    </Button>
                    <Button
                      variant="outlined"
                      color="error"
                      size="small"
                      startIcon={<Delete />}
                      onClick={handleDelete}
                    >
                      삭제
                    </Button>
                  </Box>
                )}
              </Box>

              <Divider sx={{ my: 2 }} />

              {/* 게시글 내용 */}
              <Box sx={{ mb: 4 }}>
                <Box
                  sx={{
                    '& .ql-editor': {
                      padding: 0,
                      border: 'none',
                      backgroundColor: 'transparent',
                      fontFamily: 'inherit',
                      fontSize: 'inherit',
                      lineHeight: 1.6,
                    },
                    '& p': {
                      margin: '0.5em 0',
                    },
                    '& h1, & h2, & h3, & h4, & h5, & h6': {
                      margin: '1em 0 0.5em 0',
                      fontWeight: 'bold',
                    },
                    '& blockquote': {
                      borderLeft: '4px solid #ccc',
                      margin: '1em 0',
                      padding: '0.5em 1em',
                      backgroundColor: '#f9f9f9',
                    },
                    '& ul, & ol': {
                      margin: '0.5em 0',
                      paddingLeft: '2em',
                    },
                    '& li': {
                      margin: '0.2em 0',
                    },
                    '& a': {
                      color: 'primary.main',
                      textDecoration: 'underline',
                    },
                    '& img': {
                      maxWidth: '100%',
                      height: 'auto',
                    },
                  }}
                  dangerouslySetInnerHTML={{ __html: sanitizeHtml(strategy.content) }}
                />
              </Box>

              {/* 좋아요 버튼 */}
              <Box sx={{ display: 'flex', justifyContent: 'center', gap: 2, mb: 4 }}>
                <Button
                  variant={isLiked ? "outlined" : "contained"}
                  color="primary"
                  startIcon={<ThumbUp />}
                  onClick={handleLikeToggle}
                  disabled={isLiked}
                  sx={{ 
                    minWidth: 120,
                    opacity: isLiked ? 0.6 : 1,
                    '&:hover': {
                      opacity: isLiked ? 0.6 : 0.8
                    }
                  }}
                >
                  좋아요 {isLiked && '(완료)'}
                </Button>
                <Button
                  variant={isLiked ? "contained" : "outlined"}
                  color="error"
                  startIcon={<ThumbDown />}
                  onClick={handleLikeToggle}
                  disabled={!isLiked}
                  sx={{ 
                    minWidth: 120,
                    opacity: !isLiked ? 0.6 : 1,
                    '&:hover': {
                      opacity: !isLiked ? 0.6 : 0.8
                    }
                  }}
                >
                  좋아요 취소 {!isLiked && '(불가)'}
                </Button>
              </Box>

              {/* 댓글 섹션 (추후 구현) */}
              <Box sx={{ mt: 4 }}>
                <Typography variant="h6" gutterBottom>
                  댓글 ({strategy.comment_count})
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  댓글 기능은 추후 구현 예정입니다.
                </Typography>
              </Box>
            </Box>
          </Stack>
          <Copyright sx={{ my: 4 }} />
        </Box>
      </Box>
    </AppTheme>
  );
} 