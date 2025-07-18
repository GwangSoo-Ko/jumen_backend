import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  TextField, 
  Button, 
  Box, 
  Alert, 
  CircularProgress, 
  FormControl, 
  InputLabel, 
  Select, 
  MenuItem, 
  Slider, 
  Typography, 
  Chip, 
  Grid,
  Autocomplete,
  Card,
  CardContent,
  Divider,
  Stack
} from '@mui/material';
import { alpha } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
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
import TextEditor from '../components/TextEditor';
import { useAuth, fetchWithAuth } from '../contexts/AuthContext';

const xThemeComponents = {
  ...chartsCustomizations,
  ...dataGridCustomizations,
  ...datePickersCustomizations,
  ...treeViewCustomizations,
};

// 전략 타입 옵션
const strategyTypes = [
  { value: 'buy', label: '매수', color: '#4caf50' },
  { value: 'sell', label: '매도', color: '#f44336' },
  { value: 'hold', label: '보유', color: '#ff9800' },
  { value: 'analysis', label: '분석', color: '#2196f3' }
];

// 보유기간 옵션
const holdingPeriods = [
  { value: 'short', label: '단기 (1개월 이하)' },
  { value: 'medium', label: '중기 (1-6개월)' },
  { value: 'long', label: '장기 (6개월 이상)' }
];

// 위험도 라벨
const riskLabels = {
  1: '매우 낮음',
  2: '낮음', 
  3: '보통',
  4: '높음',
  5: '매우 높음'
};

// 성과 평가 라벨
const performanceLabels = {
  1: '매우 낮음',
  2: '낮음',
  3: '보통', 
  4: '높음',
  5: '매우 높음'
};

export default function StrategyBoardEdit(props) {
  const { id } = useParams();
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [loading, setLoading] = useState(false);
  const [fetching, setFetching] = useState(true);
  const [error, setError] = useState('');
  const navigate = useNavigate();
  const { user } = useAuth();

  // 전략 특화 필드들
  const [strategyType, setStrategyType] = useState('');
  const [targetPrice, setTargetPrice] = useState('');
  const [riskLevel, setRiskLevel] = useState(3);
  const [performanceRating, setPerformanceRating] = useState(3);
  const [entryPrice, setEntryPrice] = useState('');
  const [exitPrice, setExitPrice] = useState('');
  const [holdingPeriod, setHoldingPeriod] = useState('');
  const [relatedStockId, setRelatedStockId] = useState(null);
  const [relatedThemeId, setRelatedThemeId] = useState(null);
  const [tags, setTags] = useState([]);
  const [tagInput, setTagInput] = useState('');

  // 주식/테마 검색용
  const [stocks, setStocks] = useState([]);
  const [themes, setThemes] = useState([]);
  const [stockSearch, setStockSearch] = useState('');
  const [themeSearch, setThemeSearch] = useState('');

  // 기존 게시글 데이터 가져오기
  const fetchPost = async () => {
    try {
      setFetching(true);
      setError('');

      const response = await fetchWithAuth(`http://localhost:8000/strategy-board/posts/${id}`);
      
      if (!response.ok) {
        if (response.status === 404) {
          throw new Error('게시글을 찾을 수 없습니다.');
        }
        throw new Error('게시글을 불러오는데 실패했습니다.');
      }

      const data = await response.json();
      
      // 작성자 확인
      if (data.user_id !== user.id) {
        alert('수정 권한이 없습니다.');
        navigate('/strategy-board');
        return;
      }

      setTitle(data.title);
      setContent(data.content);
      
      // 전략 특화 필드들 설정
      setStrategyType(data.strategy_type || '');
      setTargetPrice(data.target_price ? data.target_price.toString() : '');
      setRiskLevel(data.risk_level || 3);
      setPerformanceRating(data.performance_rating || 3);
      setEntryPrice(data.entry_price ? data.entry_price.toString() : '');
      setExitPrice(data.exit_price ? data.exit_price.toString() : '');
      setHoldingPeriod(data.holding_period || '');
      setRelatedStockId(data.related_stock_id);
      setRelatedThemeId(data.related_theme_id);
      setTags(data.tags || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setFetching(false);
    }
  };

  // 주식 검색
  const searchStocks = async (query) => {
    if (!query.trim()) return;
    
    try {
      const response = await fetchWithAuth(`http://localhost:8000/stocks/search?q=${encodeURIComponent(query)}`);
      if (response.ok) {
        const data = await response.json();
        setStocks(data);
      }
    } catch (err) {
      console.error('주식 검색 실패:', err);
    }
  };

  // 테마 검색
  const searchThemes = async (query) => {
    if (!query.trim()) return;
    
    try {
      const response = await fetchWithAuth(`http://localhost:8000/themes/search?q=${encodeURIComponent(query)}`);
      if (response.ok) {
        const data = await response.json();
        setThemes(data);
      }
    } catch (err) {
      console.error('테마 검색 실패:', err);
    }
  };

  // 태그 추가
  const handleAddTag = () => {
    if (tagInput.trim() && !tags.includes(tagInput.trim())) {
      setTags([...tags, tagInput.trim()]);
      setTagInput('');
    }
  };

  // 태그 삭제
  const handleDeleteTag = (tagToDelete) => {
    setTags(tags.filter(tag => tag !== tagToDelete));
  };

  useEffect(() => {
    fetchPost();
  }, [id]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!title.trim()) {
      setError('제목을 입력해주세요.');
      return;
    }
    
    if (!content.trim()) {
      setError('내용을 입력해주세요.');
      return;
    }

    try {
      setLoading(true);
      setError('');

      const postData = {
        title: title.trim(),
        content: content.trim(),
        strategy_type: strategyType || null,
        target_price: targetPrice ? parseFloat(targetPrice) : null,
        risk_level: riskLevel,
        performance_rating: performanceRating,
        entry_price: entryPrice ? parseFloat(entryPrice) : null,
        exit_price: exitPrice ? parseFloat(exitPrice) : null,
        holding_period: holdingPeriod || null,
        related_stock_id: relatedStockId,
        related_theme_id: relatedThemeId,
        tags: tags.length > 0 ? tags : null
      };

      const response = await fetchWithAuth(`http://localhost:8000/strategy-board/posts/${id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(postData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || '게시글 수정에 실패했습니다.');
      }

      alert('전략이 수정되었습니다!');
      navigate(`/strategy-board/${id}`);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };



  if (fetching) {
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
              <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 400 }}>
                <CircularProgress />
              </Box>
            </Stack>
          </Box>
        </Box>
      </AppTheme>
    );
  }

  if (error) {
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
              <Alert severity="error" sx={{ maxWidth: 600 }}>
                {error}
              </Alert>
            </Stack>
          </Box>
        </Box>
      </AppTheme>
    );
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
          <Box sx={{ p: 3, maxWidth: 1000, mx: 'auto', mt: { xs: 8, md: 2 } }}>
            <Header />
            
            {/* 페이지 제목 */}
            <Box sx={{ mb: 3, textAlign: 'center' }}>
              <Typography variant="h4" component="h1" gutterBottom sx={{ fontWeight: 'bold' }}>
                📝 전략 게시판 수정
              </Typography>
              <Typography variant="body1" color="text.secondary">
                투자 전략을 수정해보세요
              </Typography>
            </Box>
            
            {error && (
              <Alert severity="error" sx={{ mb: 3 }}>
                {error}
              </Alert>
            )}

            <Box component="form" onSubmit={handleSubmit}>
              <Stack spacing={3}>
                {/* 1. 기본 정보 카드 */}
                <Card elevation={2}>
                  <CardContent>
                    <Typography variant="h6" gutterBottom sx={{ fontWeight: 'bold', color: 'primary.main' }}>
                      📝 기본 정보
                    </Typography>
                    <TextField
                      fullWidth
                      label="전략 제목"
                      variant="outlined"
                      value={title}
                      onChange={(e) => setTitle(e.target.value)}
                      placeholder="예: 삼성전자 이동평균선 돌파 매수 전략"
                      disabled={loading}
                      required
                      sx={{ mt: 1 }}
                    />
                  </CardContent>
                </Card>

                {/* 2. 전략 개요 카드 */}
                <Card elevation={2}>
                  <CardContent>
                    <Typography variant="h6" gutterBottom sx={{ fontWeight: 'bold', color: 'primary.main' }}>
                      🎯 전략 개요
                    </Typography>
                    <Grid container spacing={2}>
                      <Grid item xs={12} md={6}>
                        <FormControl fullWidth disabled={loading}>
                          <InputLabel>전략 타입</InputLabel>
                          <Select
                            value={strategyType}
                            onChange={(e) => setStrategyType(e.target.value)}
                            label="전략 타입"
                          >
                            {strategyTypes.map((type) => (
                              <MenuItem key={type.value} value={type.value}>
                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                  <Box sx={{ 
                                    width: 12, 
                                    height: 12, 
                                    borderRadius: '50%', 
                                    backgroundColor: type.color 
                                  }} />
                                  {type.label}
                                </Box>
                              </MenuItem>
                            ))}
                          </Select>
                        </FormControl>
                      </Grid>
                      <Grid item xs={12} md={6}>
                        <FormControl fullWidth disabled={loading}>
                          <InputLabel>보유기간</InputLabel>
                          <Select
                            value={holdingPeriod}
                            onChange={(e) => setHoldingPeriod(e.target.value)}
                            label="보유기간"
                          >
                            {holdingPeriods.map((period) => (
                              <MenuItem key={period.value} value={period.value}>
                                {period.label}
                              </MenuItem>
                            ))}
                          </Select>
                        </FormControl>
                      </Grid>
                    </Grid>
                  </CardContent>
                </Card>

                {/* 3. 가격 정보 카드 */}
                <Card elevation={2}>
                  <CardContent>
                    <Typography variant="h6" gutterBottom sx={{ fontWeight: 'bold', color: 'primary.main' }}>
                      💰 가격 정보
                    </Typography>
                    <Grid container spacing={2}>
                      <Grid item xs={12} md={4}>
                        <TextField
                          fullWidth
                          label="진입가"
                          variant="outlined"
                          type="number"
                          value={entryPrice}
                          onChange={(e) => setEntryPrice(e.target.value)}
                          placeholder="0"
                          disabled={loading}
                          InputProps={{
                            startAdornment: <Typography variant="body2">₩</Typography>,
                          }}
                        />
                      </Grid>
                      <Grid item xs={12} md={4}>
                        <TextField
                          fullWidth
                          label="목표가"
                          variant="outlined"
                          type="number"
                          value={targetPrice}
                          onChange={(e) => setTargetPrice(e.target.value)}
                          placeholder="0"
                          disabled={loading}
                          InputProps={{
                            startAdornment: <Typography variant="body2">₩</Typography>,
                          }}
                        />
                      </Grid>
                      <Grid item xs={12} md={4}>
                        <TextField
                          fullWidth
                          label="청산가"
                          variant="outlined"
                          type="number"
                          value={exitPrice}
                          onChange={(e) => setExitPrice(e.target.value)}
                          placeholder="0"
                          disabled={loading}
                          InputProps={{
                            startAdornment: <Typography variant="body2">₩</Typography>,
                          }}
                        />
                      </Grid>
                    </Grid>
                  </CardContent>
                </Card>

                {/* 4. 리스크 & 성과 평가 카드 */}
                <Card elevation={2}>
                  <CardContent>
                    <Typography variant="h6" gutterBottom sx={{ fontWeight: 'bold', color: 'primary.main' }}>
                      ⚖️ 리스크 & 성과 평가
                    </Typography>
                    <Grid container spacing={3}>
                      <Grid item xs={12} md={6}>
                        <Box>
                          <Typography gutterBottom variant="subtitle1" sx={{ fontWeight: 'medium' }}>
                            위험도: {riskLabels[riskLevel]}
                          </Typography>
                          <Slider
                            value={riskLevel}
                            onChange={(e, newValue) => setRiskLevel(newValue)}
                            min={1}
                            max={5}
                            marks
                            valueLabelDisplay="auto"
                            disabled={loading}
                            sx={{ mt: 1 }}
                          />
                        </Box>
                      </Grid>
                      <Grid item xs={12} md={6}>
                        <Box>
                          <Typography gutterBottom variant="subtitle1" sx={{ fontWeight: 'medium' }}>
                            예상 성과: {performanceLabels[performanceRating]}
                          </Typography>
                          <Slider
                            value={performanceRating}
                            onChange={(e, newValue) => setPerformanceRating(newValue)}
                            min={1}
                            max={5}
                            marks
                            valueLabelDisplay="auto"
                            disabled={loading}
                            sx={{ mt: 1 }}
                          />
                        </Box>
                      </Grid>
                    </Grid>
                  </CardContent>
                </Card>

                {/* 5. 관련 정보 카드 */}
                <Card elevation={2}>
                  <CardContent>
                    <Typography variant="h6" gutterBottom sx={{ fontWeight: 'bold', color: 'primary.main' }}>
                      🔗 관련 정보
                    </Typography>
                    <Grid container spacing={2}>
                      <Grid item xs={12} md={6}>
                        <Autocomplete
                          options={stocks}
                          getOptionLabel={(option) => option.name || ''}
                          value={stocks.find(s => s.id === relatedStockId) || null}
                          onChange={(e, newValue) => setRelatedStockId(newValue?.id || null)}
                          onInputChange={(e, newInputValue) => {
                            setStockSearch(newInputValue);
                            if (newInputValue.length > 1) {
                              searchStocks(newInputValue);
                            }
                          }}
                          renderInput={(params) => (
                            <TextField
                              {...params}
                              label="관련 주식"
                              placeholder="주식명을 검색하세요"
                              disabled={loading}
                            />
                          )}
                          noOptionsText="검색 결과가 없습니다"
                        />
                      </Grid>
                      <Grid item xs={12} md={6}>
                        <Autocomplete
                          options={themes}
                          getOptionLabel={(option) => option.name || ''}
                          value={themes.find(t => t.id === relatedThemeId) || null}
                          onChange={(e, newValue) => setRelatedThemeId(newValue?.id || null)}
                          onInputChange={(e, newInputValue) => {
                            setThemeSearch(newInputValue);
                            if (newInputValue.length > 1) {
                              searchThemes(newInputValue);
                            }
                          }}
                          renderInput={(params) => (
                            <TextField
                              {...params}
                              label="관련 테마"
                              placeholder="테마명을 검색하세요"
                              disabled={loading}
                            />
                          )}
                          noOptionsText="검색 결과가 없습니다"
                        />
                      </Grid>
                    </Grid>
                  </CardContent>
                </Card>

                {/* 6. 태그 카드 */}
                <Card elevation={2}>
                  <CardContent>
                    <Typography variant="h6" gutterBottom sx={{ fontWeight: 'bold', color: 'primary.main' }}>
                      🏷️ 태그
                    </Typography>
                    <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                      <TextField
                        label="태그 추가"
                        variant="outlined"
                        size="small"
                        value={tagInput}
                        onChange={(e) => setTagInput(e.target.value)}
                        onKeyPress={(e) => {
                          if (e.key === 'Enter') {
                            e.preventDefault();
                            handleAddTag();
                          }
                        }}
                        disabled={loading}
                        placeholder="예: 이동평균선, RSI, 모멘텀"
                        sx={{ flexGrow: 1 }}
                      />
                      <Button
                        variant="outlined"
                        onClick={handleAddTag}
                        disabled={loading || !tagInput.trim()}
                        sx={{ minWidth: 80 }}
                      >
                        추가
                      </Button>
                    </Box>
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                      {tags.map((tag) => (
                        <Chip
                          key={tag}
                          label={tag}
                          onDelete={() => handleDeleteTag(tag)}
                          disabled={loading}
                          color="primary"
                          variant="outlined"
                        />
                      ))}
                      {tags.length === 0 && (
                        <Typography variant="body2" color="text.secondary">
                          관련 태그를 추가해보세요
                        </Typography>
                      )}
                    </Box>
                  </CardContent>
                </Card>

                {/* 7. 전략 내용 카드 */}
                <Card elevation={2}>
                  <CardContent>
                    <Typography variant="h6" gutterBottom sx={{ fontWeight: 'bold', color: 'primary.main' }}>
                      📄 전략 내용
                    </Typography>
                    <TextEditor 
                      value={content} 
                      onChange={setContent}
                      disabled={loading}
                    />
                  </CardContent>
                </Card>

                {/* 8. 액션 버튼 */}
                <Card elevation={2}>
                  <CardContent>
                    <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center' }}>
                      <Button 
                        type="submit" 
                        variant="contained" 
                        color="primary"
                        size="large"
                        disabled={loading}
                        startIcon={loading ? <CircularProgress size={20} /> : null}
                        sx={{ 
                          minWidth: 150,
                          py: 1.5,
                          px: 4,
                          fontSize: '1.1rem',
                          fontWeight: 'bold'
                        }}
                      >
                        {loading ? '수정 중...' : '전략 수정'}
                      </Button>
                      <Button 
                        variant="outlined" 
                        onClick={() => navigate(`/strategy-board/${id}`)}
                        disabled={loading}
                        size="large"
                        sx={{ 
                          minWidth: 120,
                          py: 1.5,
                          px: 4,
                          fontSize: '1.1rem'
                        }}
                      >
                        취소
                      </Button>
                    </Box>
                  </CardContent>
                </Card>
              </Stack>
            </Box>
          </Box>
        </Box>
      </Box>
    </AppTheme>
  );
} 