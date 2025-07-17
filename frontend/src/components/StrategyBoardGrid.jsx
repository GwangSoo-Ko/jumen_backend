import * as React from 'react';
import { DataGrid } from '@mui/x-data-grid';
import Box from '@mui/material/Box';
import Copyright from '../internals/components/Copyright';
import { useNavigate } from 'react-router-dom';
import { Button } from '@mui/material';
import { useAuth } from '../contexts/AuthContext';

const columns = [
  { field: 'id', headerName: 'ID', width: 70 },
  { field: 'title', headerName: '전략 제목', flex: 1 },
  { field: 'author', headerName: '작성자', width: 120 },
  { field: 'createdAt', headerName: '작성일', width: 150 },
];

const rows = [
  { id: 1, title: '이동평균선 돌파 전략', author: 'user1', createdAt: '2024-06-01' },
  { id: 2, title: 'RSI 기반 매매', author: 'user2', createdAt: '2024-06-02' },
  { id: 3, title: '퀀트 모멘텀 전략', author: 'user3', createdAt: '2024-06-03' },
];

export default function StrategyBoardGrid(props) {
  const { user } = useAuth();
  const navigate = useNavigate();
  const handleRowClick = (params) => {
    if (!user) {
      alert('로그인 후 상세 내용을 볼 수 있습니다.');
      // navigate('/sign-in');
      return;
    }
    navigate(`/strategy-board/${params.id}`);
  };
  return (
    <Box sx={{ width: '100%', maxWidth: { sm: '100%', md: '1700px' }, mx: 'auto', py: 4 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
        <h1 style={{ margin: '0 16px 0 0' }}>전략 게시판</h1>
        <Button
          variant="outlined"
          size="small"
          onClick={() => navigate('/strategy-board/write')}
          disabled={!user}
        >
          글쓰기
        </Button>
      </Box>
      <DataGrid
        rows={rows}
        columns={columns}
        pageSize={5}
        rowsPerPageOptions={[5, 10, 20]}
        disableSelectionOnClick
        onRowClick={handleRowClick}
      />
      <Copyright sx={{ my: 4 }} />
    </Box>
  );
} 