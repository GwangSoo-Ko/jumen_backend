import * as React from 'react';
import { useState, useEffect } from 'react';
import { DataGrid } from '@mui/x-data-grid';
import Box from '@mui/material/Box';
import Copyright from '../internals/components/Copyright';
import { useNavigate } from 'react-router-dom';
import { Button, TextField, Select, MenuItem, FormControl, InputLabel, CircularProgress, Alert } from '@mui/material';
import { useAuth, fetchWithAuth } from '../contexts/AuthContext';

const columns = [
  { field: 'id', headerName: 'ID', width: 70 },
  { field: 'title', headerName: '전략 제목', flex: 1 },
  { field: 'user_nickname', headerName: '작성자', width: 120 },
  { field: 'view_count', headerName: '조회수', width: 100 },
  { field: 'like_count', headerName: '좋아요', width: 100 },
  { field: 'comment_count', headerName: '댓글', width: 100 },
  { field: 'crt_date', headerName: '작성일', width: 180, 
    valueFormatter: (params) => new Date(params).toLocaleString('ko-KR', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    }) },
];

export default function StrategyBoardGrid(props) {
  const { user } = useAuth();
  const navigate = useNavigate();
  
  // 상태 관리
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [search, setSearch] = useState('');
  const [sort, setSort] = useState('latest');
  const [total, setTotal] = useState(0);

  // API 호출 함수
  const fetchPosts = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const params = new URLSearchParams({
        page: page.toString(),
        size: pageSize.toString(),
        sort: sort
      });
      
      if (search.trim()) {
        params.append('search', search.trim());
      }

      const response = await fetchWithAuth(`http://localhost:8000/strategy-board/posts?${params}`);
      
      if (!response.ok) {
        throw new Error('게시글을 불러오는데 실패했습니다.');
      }

      const data = await response.json();
      setPosts(data.items);
      setTotal(data.total);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // 컴포넌트 마운트 시 및 의존성 변경 시 API 호출
  useEffect(() => {
    fetchPosts();
  }, [page, pageSize, sort, search]);

  const handleRowClick = (params) => {
    if (!user) {
      alert('로그인 후 상세 내용을 볼 수 있습니다.');
      return;
    }
    navigate(`/strategy-board/${params.id}`);
  };

  const handleSearch = (event) => {
    setSearch(event.target.value);
    setPage(1); // 검색 시 첫 페이지로 이동
  };

  const handleSortChange = (event) => {
    setSort(event.target.value);
    setPage(1); // 정렬 변경 시 첫 페이지로 이동
  };

  if (loading && posts.length === 0) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 400 }}>
        <CircularProgress />
      </Box>
    );
  }

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

      {/* 검색 및 정렬 컨트롤 */}
      <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
        <TextField
          label="검색"
          variant="outlined"
          size="small"
          value={search}
          onChange={handleSearch}
          placeholder="제목 또는 내용으로 검색"
          sx={{ minWidth: 200 }}
        />
        <FormControl size="small" sx={{ minWidth: 120 }}>
          <InputLabel>정렬</InputLabel>
          <Select value={sort} onChange={handleSortChange} label="정렬">
            <MenuItem value="latest">최신순</MenuItem>
            <MenuItem value="oldest">오래된순</MenuItem>
            <MenuItem value="views">조회수순</MenuItem>
            <MenuItem value="likes">좋아요순</MenuItem>
            <MenuItem value="comments">댓글순</MenuItem>
          </Select>
        </FormControl>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <DataGrid
        rows={posts}
        columns={columns}
        pageSize={pageSize}
        rowsPerPageOptions={[5, 10, 20, 50]}
        disableSelectionOnClick
        onRowClick={handleRowClick}
        pagination
        paginationMode="server"
        rowCount={total}
        page={page - 1}
        onPageChange={(newPage) => setPage(newPage + 1)}
        onPageSizeChange={(newPageSize) => {
          setPageSize(newPageSize);
          setPage(1);
        }}
        loading={loading}
        sx={{
          '& .MuiDataGrid-row': {
            cursor: 'pointer',
            '&:hover': {
              backgroundColor: 'rgba(0, 0, 0, 0.04)',
            },
          },
        }}
      />
      <Copyright sx={{ my: 4 }} />
    </Box>
  );
} 