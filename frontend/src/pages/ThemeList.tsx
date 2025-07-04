import React, { useEffect, useState } from 'react';
import ThemeCard from '../components/ThemeCard';
import { useNavigate } from 'react-router-dom';

interface Theme {
  id: number;
  theme_name: string;
  description: string;
  change_rate: number;
  avg_change_rate_3days: number;
  up_ticker_count: number;
  neutral_ticker_count: number;
  down_ticker_count: number;
  detail_url: string;
}

const ThemeList: React.FC = () => {
  const [themes, setThemes] = useState<Theme[]>([]);
  const navigate = useNavigate();

  useEffect(() => {
    fetch('http://localhost:8000/themes') // FastAPI 서버 주소에 맞게 수정
      .then(res => res.json())
      .then(data => setThemes(data));
  }, []);

  return (
    <div style={{ padding: '2rem', background: '#f5f7fa', minHeight: '100vh' }}>
      <h2 style={{ color: '#222', marginBottom: 32, fontWeight: 800, fontSize: 28 }}>테마(섹터) 목록</h2>
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 24, justifyContent: 'flex-start' }}>
        {themes.map(theme => (
          <ThemeCard
            key={theme.id}
            name={theme.theme_name}
            description={theme.description}
            change_rate={theme.change_rate}
            avg_change_rate_3days={theme.avg_change_rate_3days}
            up_ticker_count={theme.up_ticker_count}
            neutral_ticker_count={theme.neutral_ticker_count}
            down_ticker_count={theme.down_ticker_count}
            companyCount={theme.up_ticker_count + theme.neutral_ticker_count + theme.down_ticker_count}
            onClick={() => navigate(`/themes/${theme.id}`)}
          />
        ))}
      </div>
    </div>
  );
};

export default ThemeList; 