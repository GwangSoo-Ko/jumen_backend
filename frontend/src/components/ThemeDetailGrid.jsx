import * as React from 'react';
import { DataGrid } from '@mui/x-data-grid';

const columns = [
  { field: 'ticker', headerName: '티커', width: 120, align: 'center', headerAlign: 'center' },
  { field: 'name', headerName: '종목명', width: 120, align: 'center', headerAlign: 'center' },
  { field: 'current_price', headerName: '현재가', width: 120, align: 'center', headerAlign: 'center',
    valueFormatter: (params) => {
      const value = Number(params);
      if (isNaN(value)) return '-';
      return value.toLocaleString();
    },
    cellClassName: (params) =>
      Number(params.row.change_rate) > 0 ? 'mui-red'
      : Number(params.row.change_rate) < 0 ? 'mui-blue'
      : '',
  },
  { field: 'diff_price', headerName: '전일대비', width: 120, align: 'center', headerAlign: 'center',
    valueFormatter: (params) => {
      const value = Number(params);
      if (isNaN(value)) return '-';
      return value.toLocaleString();
    },
    cellClassName: (params) =>
      Number(params.row.change_rate) > 0 ? 'mui-red'
      : Number(params.row.change_rate) < 0 ? 'mui-blue'
      : '',
  },
  {
    field: 'change_rate',
    headerName: '등락률',
    width: 120, align: 'center', headerAlign: 'center',
    valueFormatter: (params) => {
      const value = Number(params);
      if (isNaN(value)) return '-';
      return (value > 0 ? '+' : value < 0 ? '' : '') + (value * 100).toFixed(2) + '%';
    },
    cellClassName: (params) =>
      Number(params.value) > 0 ? 'mui-red' : Number(params.value) < 0 ? 'mui-blue' : '',
  },
  { field: 'volume', headerName: '거래량', width: 120, align: 'center', headerAlign: 'center',
    valueFormatter: (params) => {
      const value = Number(params);
      if (isNaN(value)) return '-';
      return value.toLocaleString();
    },
  },
  { field: 'trading_value', headerName: '거래대금', width: 120, align: 'center', headerAlign: 'center',
    
    valueFormatter: (params) => {
      const value = Number(params);
      if (isNaN(value)) return '-';
      return value.toLocaleString();
    },
  },
  { field: 'volume_yesterday', headerName: '전일거래량', width: 120, align: 'center', headerAlign: 'center',
    
    valueFormatter: (params) => {
      const value = Number(params);
      if (isNaN(value)) return '-';
      return value.toLocaleString();
    },
  },
  { field: 'description', headerName: '비고', width: 200, flex: 1, headerAlign: 'center' },
  {
    field: 'mod_date',
    headerName: '마지막 업데이트',
    width: 120,
    align: 'center',
    headerAlign: 'center',
    valueFormatter: (params) => {
      const date = new Date(params);
      const now = new Date();
      const diffMs = now - date;
      const diffSec = Math.floor(diffMs / 1000);
      const diffMin = Math.floor(diffSec / 60);
      const diffHour = Math.floor(diffMin / 60);
      const diffDay = Math.floor(diffHour / 24);

      if (isNaN(date.getTime())) return '-';
      if (diffMin < 1) return '방금 전';
      if (diffHour < 1) return `${diffMin}분 전`;
      if (diffDay < 1) return `${diffHour}시간 전`;
      return `${diffDay}일 전`;
    },
  },
];

export default function ThemeDetailGrid({ stocks }) {
  // DataGrid는 각 row에 id 필드가 필요함. stock_id를 id로 매핑.
  const rows = React.useMemo(
    () => stocks.map((row, idx) => ({ ...row, id: row.stock_id ?? idx })),
    [stocks]
  );


  return (
    <div style={{ width: '100%', height: 600 }}>
      <DataGrid
        rows={rows}
        columns={columns}
        pageSize={50}
        rowsPerPageOptions={[10, 20, 50]}
        disableSelectionOnClick
        density="compact"
        initialState={{
          sorting: {
            sortModel: [{ field: 'change_rate', sort: 'desc' }],
          },
        }}
        sx={{
          '& .mui-red': { color: '#d32f2f' },
          '& .mui-blue': { color: '#1976d2' },
        }}
      />
    </div>
  );
} 