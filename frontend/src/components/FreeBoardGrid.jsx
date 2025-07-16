import * as React from 'react';
import { DataGrid } from '@mui/x-data-grid';
import Box from '@mui/material/Box';
import Copyright from '../internals/components/Copyright';
import { useNavigate } from 'react-router-dom';
import { Button } from '@mui/material';

const columns = [
  { field: 'id', headerName: 'ID', width: 70 },
  { field: 'title', headerName: '게시글 제목', flex: 1 },
  { field: 'author', headerName: '작성자', width: 120 },
  { field: 'createdAt', headerName: '작성일', width: 150 },
];

const rows = [
  { id: 1, title: '자유롭게 소통해요', author: 'userA', createdAt: '2024-06-01' },
  { id: 2, title: '오늘의 주식 이야기', author: 'userB', createdAt: '2024-06-02' },
  { id: 3, title: '잡담 환영합니다', author: 'userC', createdAt: '2024-06-03' },
];

export default function FreeBoardGrid({ data = rows }) {
  const navigate = useNavigate();
  return (
    <Box sx={{ width: '100%', maxWidth: { sm: '100%', md: '1700px' }, mx: 'auto', py: 4 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
        <h1 style={{ margin: '0 16px 0 0' }}>자유 게시판</h1>
        <Button variant="outlined" size="small" onClick={() => navigate('/free-board/write')}>
          글쓰기
        </Button>
      </Box>
      <DataGrid
        rows={data}
        columns={columns}
        pageSize={5}
        rowsPerPageOptions={[5, 10, 20]}
        disableSelectionOnClick
        onRowClick={(params) => navigate(`/free-board/${params.id}`)}
      />
      <Copyright sx={{ my: 4 }} />
    </Box>
  );
} 