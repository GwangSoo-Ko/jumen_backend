import * as React from 'react';
import { useState, useEffect } from 'react';
import Grid from '@mui/material/Grid';
import Box from '@mui/material/Box';
import Stack from '@mui/material/Stack';
import Typography from '@mui/material/Typography';
import Copyright from '../internals/components/Copyright';
import ChartUserByCountry from './ChartUserByCountry';
import CustomizedTreeView from './CustomizedTreeView';
import CustomizedDataGrid from './CustomizedDataGrid';
import HighlightedCard from './HighlightedCard';
import PageViewsBarChart from './PageViewsBarChart';
import SessionsChart from './SessionsChart';
import StatCard from './StatCard';
import IndexChart from './IndexChart';
import Select from '@mui/material/Select';
import MenuItem from '@mui/material/MenuItem';
import Button from '@mui/material/Button';

const data = [
  {
    title: 'Users',
    value: '14k',
    interval: 'Last 30 days',
    trend: 'up',
    data: [
      20, 24, 220, 260, 240, 380, 100, 240, 280, 240, 300, 340, 320, 360, 340, 380,
      360, 400, 380, 420, 400, 640, 340, 460, 440, 480, 460, 600, 880, 920,
    ],
  },
  {
    title: 'Conversions',
    value: '325',
    interval: 'Last 30 days',
    trend: 'down',
    data: [
      1640, 1250, 970, 1130, 1050, 900, 720, 1080, 900, 450, 920, 820, 840, 600, 820,
      780, 800, 760, 380, 740, 660, 620, 840, 500, 520, 480, 400, 360, 300, 220,
    ],
  },
  {
    title: 'Event count',
    value: '200k',
    interval: 'Last 30 days',
    trend: 'neutral',
    data: [
      500, 400, 510, 530, 520, 600, 530, 520, 510, 730, 520, 510, 530, 620, 510, 530,
      520, 410, 530, 520, 610, 530, 520, 610, 530, 420, 510, 430, 520, 510,
    ],
  },
];

export default function MainGrid() {
  const [statData, setStatData] = useState([]);
  const [nDays, setNDays] = useState(30);
  const [appliedNDays, setAppliedNDays] = useState(30);

  useEffect(() => {
    fetch(`http://localhost:8000/index_all?n_days=${appliedNDays}`)
      .then(response => {
        if (!response.ok) throw new Error('네트워크 오류');
        return response.json();
      })
      .then(data => {
        if (!Array.isArray(data)) throw new Error('데이터 형식 오류');
        // 각 index별로 StatCard용 데이터 생성
        const statCards = data.map(idx => {
          const closeArr = idx.ohlcv.map(item => item.close);
          const dateArr = idx.ohlcv.map(item => item.ymd.split('T')[0]);
          const lastClose = closeArr.length > 0 ? closeArr[closeArr.length - 1] : '-';
          let trend = 'neutral';
          if (closeArr.length > 1) {
            if (closeArr[closeArr.length - 1] > closeArr[0]) trend = 'up';
            else if (closeArr[closeArr.length - 1] < closeArr[0]) trend = 'down';
          }
          return {
            index_id: idx.index_id,
            title: idx.description,
            value: lastClose,
            interval: `Last ${appliedNDays} days`,
            trend,
            data: closeArr,
            dates: dateArr,
          };
        });
        statCards.sort((a, b) => a.index_id - b.index_id);
        setStatData(statCards);
      })
      .catch(err => {
        setStatData([]);
        console.error(err);
      });
  }, [appliedNDays]);

  return (
    <Box sx={{ width: '100%', maxWidth: { sm: '100%', md: '1700px' }, mx: 'auto', py: 4  }}>
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
        <h1 style={{ margin: '0 16px 0 0' }}>Market Overview</h1>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <Select
          value={nDays}
          onChange={e => setNDays(Number(e.target.value))}
          size="small"
        >
          <MenuItem value={7}>7일</MenuItem>
          <MenuItem value={30}>30일</MenuItem>
          <MenuItem value={60}>60일</MenuItem>
          <MenuItem value={90}>90일</MenuItem>
          <MenuItem value={180}>180일</MenuItem>
          <MenuItem value={365}>1년</MenuItem>
        </Select>
        <Button
          variant="outlined"
          size="small"  
          onClick={() => setAppliedNDays(nDays)}
          disabled={nDays === appliedNDays}
        >
          적용
        </Button>
        </Box>
      </Box>
      <Grid
        container
        spacing={2}
        columns={12}
        sx={{ mb: (theme) => theme.spacing(2) }}
      >
        {statData.map((card, index) => (
          <Grid key={index} size={{ xs: 12, sm: 6, lg: 3 }}>
            <StatCard {...card} />
          </Grid>
        ))}
        {/* <Grid size={{ xs: 12, sm: 6, lg: 3 }}>
          <HighlightedCard />
        </Grid>
        <Grid size={{ xs: 12, md: 6 }}>
          <SessionsChart />
        </Grid>
        <Grid size={{ xs: 12, md: 6 }}>
          <PageViewsBarChart />
        </Grid> */}
      </Grid>
      {/* <Typography component="h2" variant="h6" sx={{ mb: 2 }}>
        Details
      </Typography>
      <Grid container spacing={2} columns={12}>
        <Grid size={{ xs: 12, lg: 9 }}>
          <CustomizedDataGrid />
        </Grid>
        <Grid size={{ xs: 12, lg: 3 }}>
          <Stack gap={2} direction={{ xs: 'column', sm: 'row', lg: 'column' }}>
            <CustomizedTreeView />
            <ChartUserByCountry />
          </Stack>
        </Grid>
      </Grid> */}
      <Copyright sx={{ my: 4 }} />
    </Box>
  );
}
