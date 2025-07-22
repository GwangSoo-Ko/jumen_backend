import React, { useEffect, useState } from 'react';
import { Box, Grid, Typography } from '@mui/material';
import SectorCard from './SectorCard';
import { useNavigate } from 'react-router-dom';
import Copyright from '../internals/components/Copyright';

export default function SectorGrid() {
  const [sectors, setSectors] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    fetch('http://localhost:8000/sectors') // FastAPI 서버 주소에 맞게 수정
      .then(res => res.json())
      .then(data => setSectors(data));
  }, []);
  

  return (
    <Box sx={{ width: '100%', maxWidth: { sm: '100%', md: '1700px' }, mx: 'auto', py: 4 }}>
      <h1 style={{ margin: '0 0 8px 0' }}>업종 목록</h1>
      <Grid container spacing={3} columns={12}>
        {sectors.map(sector => (
          <Grid size={{ xs: 12, sm: 6, md: 4, lg: 3 }} key={sector.id}>
            <SectorCard
              name={sector.sector_name}
              change_rate={sector.change_rate}  
              up_ticker_count={sector.up_ticker_count}
              neutral_ticker_count={sector.neutral_ticker_count}
              down_ticker_count={sector.down_ticker_count}
              companyCount={sector.up_ticker_count + sector.neutral_ticker_count + sector.down_ticker_count}
              onClick={() => navigate(`/sectors/${sector.id}`)}
            />
          </Grid>
        ))}
      </Grid>
      <Copyright sx={{ my: 4 }} />
    </Box>
  );    
}