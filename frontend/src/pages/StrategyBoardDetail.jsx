import React from 'react';
import { useParams } from 'react-router-dom';
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

const xThemeComponents = {
  ...chartsCustomizations,
  ...dataGridCustomizations,
  ...datePickersCustomizations,
  ...treeViewCustomizations,
};

const sampleStrategies = [
  { id: 1, title: '이동평균선 돌파 전략', author: 'user1', createdAt: '2024-06-01', content: '이동평균선을 돌파할 때 매수하는 전략입니다.' },
  { id: 2, title: 'RSI 기반 매매', author: 'user2', createdAt: '2024-06-02', content: 'RSI 지표를 활용한 매매 전략입니다.' },
  { id: 3, title: '퀀트 모멘텀 전략', author: 'user3', createdAt: '2024-06-03', content: '모멘텀을 활용한 퀀트 전략입니다.' },
];

export default function StrategyBoardDetail(props) {
  const { id } = useParams();
  const strategy = sampleStrategies.find((s) => String(s.id) === String(id));

  if (!strategy) {
    return <div style={{ padding: '2rem' }}><h2>전략을 찾을 수 없습니다.</h2></div>;
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
              <h1>{strategy.title}</h1>
              <div style={{ color: '#888', marginBottom: 8 }}>
                작성자: {strategy.author} | 작성일: {strategy.createdAt}
              </div>
              <hr />
              <div style={{ marginTop: 24, fontSize: '1.1rem' }}>{strategy.content}</div>
            </div>
          </Stack>
        </Box>
      </Box>
    </AppTheme>
  );
} 