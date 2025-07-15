import React, { useEffect, useState } from 'react';
import { LineChart } from '@mui/x-charts/LineChart';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';

export default function IndexChart({ indexId = 1 }) {
  const [chartData, setChartData] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => { 
    fetch(`http://localhost:8000/index/${indexId}`)
      .then(response => {
        if (!response.ok) throw new Error('네트워크 오류');
        return response.json();
      })
      .then(data => {
        if (!Array.isArray(data)) throw new Error('데이터 형식 오류');
        const formatted = data.map(item => {
            const formattedYmd = item.ymd.split('T')[0];
            return {
            x: formattedYmd,
            y: item.close,
            };
        });
        setChartData(formatted);
        setError(null);
      })
      .catch(err => {
        setChartData([]);
        setError(err.message);
        console.error(err);
      });
  }, [indexId]);

  return (
    <Box sx={{ width: '100%', height: 400, my: 2 }}>
      <Typography variant="h6" sx={{ mb: 2 }}>
        지수 종가 추이
      </Typography>
      {error && (
        <Typography color="error">{error}</Typography>
      )}
      {chartData.length === 0 && !error && (
        <Typography color="text.secondary">데이터가 없습니다.</Typography>
      )}
      {chartData.length > 0 && (
        <LineChart
          dataset={chartData}
          series={[{ dataKey: 'y', label: '종가', showMark: false}]}
          xAxis={[{ scaleType: 'point', dataKey: 'x', label: '날짜' }]}
          yAxis={[{ label: '종가' }]}
          height={350}
          margin={{ top: 20, right: 30, left: 40, bottom: 40 }}
        />
      )}
    </Box>
  );
}