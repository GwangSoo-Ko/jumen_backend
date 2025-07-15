import React, { useEffect, useState } from 'react';
import { useParams, useLocation } from 'react-router-dom';
import { alpha } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import Box from '@mui/material/Box';
import Stack from '@mui/material/Stack';
import AppNavbar from '../components/AppNavbar';
import Header from '../components/Header';
import SideMenu from '../components/SideMenu';
import AppTheme from '../shared-theme/AppTheme';
import ThemeDetailGrid from '../components/ThemeDetailGrid';
import Copyright from '../internals/components/Copyright';
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

export default function ThemeDetail(props) {
  const { id } = useParams();
  const location = useLocation();
  const [stocks, setStocks] = useState([]);
  const [themeName, setThemeName] = useState('');
  const [themeDescription, setThemeDescription] = useState('');

  useEffect(() => {
    if (location.state && location.state.description) {
      setThemeDescription(location.state.description);
    }
    fetch(`http://localhost:8000/themes/${id}`)
      .then(res => res.json())
      .then(data => {
        setStocks(data);
        if (data.length > 0) setThemeName(data[0].theme_name);
      });
  }, [id, location.state]);

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
            <Box sx={{ width: '100%', maxWidth: { sm: '100%', md: '1700px' } }}>
              <h3 style={{ margin: '24px 0 8px 0' }}>테마 상세 페이지</h3>
              <h1 style={{ margin: '0 0 8px 0' }}>
                {themeName} <span style={{ color: '#555', fontSize: 16 }}>(Theme ID: {id})</span>
              </h1>
              <p style={{ margin: '0 0 24px 0', color: '#555', fontSize: 16 }}>{themeDescription}</p>
              <ThemeDetailGrid stocks={stocks} />
            </Box>
            <Box sx={{ width: '100%', display: 'flex', justifyContent: 'center', mt: 4 }}>
              <Copyright sx={{ my: 0, textAlign: 'center' }} />
            </Box>
          </Stack>
        </Box>
      </Box>
    </AppTheme>
  );
} 