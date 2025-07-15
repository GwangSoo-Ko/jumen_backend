import React, { useEffect, useState } from 'react';
import { Box, Grid, Typography } from '@mui/material';
import ThemeCard from '../../components/ThemeCard';
import { useNavigate } from 'react-router-dom';
import Copyright from '../internals/components/Copyright';

export default function ThemeGrid() {
  const [themes, setThemes] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    fetch('http://localhost:8000/themes') // FastAPI 서버 주소에 맞게 수정
      .then(res => res.json())
      .then(data => setThemes(data));
  }, []);

  return (
    <Box sx={{ width: '100%', maxWidth: { sm: '100%', md: '1700px' }, mx: 'auto', py: 4 }}>
      <h1 style={{ margin: '0 0 8px 0' }}>테마(섹터) 목록</h1>
      <Grid container spacing={3} columns={12}>
        {themes.map(theme => (
          <Grid item xs={12} sm={6} md={4} lg={3} key={theme.id}>
            <ThemeCard
              name={theme.theme_name}
              description={theme.description}
              change_rate={theme.change_rate}
              avg_change_rate_3days={theme.avg_change_rate_3days}
              up_ticker_count={theme.up_ticker_count}
              neutral_ticker_count={theme.neutral_ticker_count}
              down_ticker_count={theme.down_ticker_count}
              companyCount={theme.up_ticker_count + theme.neutral_ticker_count + theme.down_ticker_count}
              onClick={() => navigate(`/themes/${theme.id}`, { state: { description: theme.description } })}
            />
          </Grid>
        ))}
      </Grid>
      <Copyright sx={{ my: 4 }} />
    </Box>
  );
}
