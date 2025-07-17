import React, { useState } from 'react';
import { TextField, Button, Box } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { alpha } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
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
import TextEditor from '../components/TextEditor';
import { useAuth } from '../contexts/AuthContext';
import { useEffect } from 'react';

const xThemeComponents = {
  ...chartsCustomizations,
  ...dataGridCustomizations,
  ...datePickersCustomizations,
  ...treeViewCustomizations,
};




export default function StrategyBoardWrite(props) {
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const navigate = useNavigate();
  const { user } = useAuth();

  useEffect(() => {
    if (!user) {
      alert('로그인 후 이용 가능합니다.');
      navigate('/sign-in');
    }
  }, [user, navigate]);

  const handleSubmit = (e) => {
    e.preventDefault();
    // 실제로는 서버에 POST 요청
    alert('전략이 등록되었습니다!');
    navigate('/strategy-board');
  };

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
                <Box component="form" onSubmit={handleSubmit} sx={{ maxWidth: 900, minWidth: 600, mx: 'auto', mt: 4 }}>
                <h1 style={{ marginBottom: 16 }}>전략 게시판 글쓰기</h1>
                <input
                    className="Subject"
                    placeholder="제목을 입력해 주세요"
                    style={{padding:'7px', marginBottom:'10px',width:'100%',border:'1px solid lightGray', fontSize:'15px'}}
                    onChange={(e)=>{setTitle(e.target.value)}}
                />      
                    
                <Box sx={{ mb: 2, minWidth: 600 }}>
                <TextEditor value={content} onChange={setContent} />
                </Box>
                <Button type="submit" variant="contained" color="primary">
                    등록
                </Button>
                </Box>
                </Stack>
        </Box>
      </Box>
    </AppTheme>
  );
} 