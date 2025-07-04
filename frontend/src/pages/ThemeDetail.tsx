import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';

interface ThemeDetail {
  stock_id: number;
  ticker: string;
  name: string;
  theme_id: number;
  theme_name: string;
  current_price?: number;
  diff_price?: number;
  change_rate?: number;
  volume?: number;
  trading_value?: number;
  volume_yesterday?: number;
  description?: string;
  crt_date?: string;
  mod_date?: string;
}

const ThemeDetail: React.FC = () => {
  const { id } = useParams();
  const [stocks, setStocks] = useState<ThemeDetail[]>([]);
  const [themeName, setThemeName] = useState<string>('');

  useEffect(() => {
    fetch(`http://localhost:8000/themes/${id}`)
      .then(res => res.json())
      .then(data => {
        setStocks(data);
        if (data.length > 0) setThemeName(data[0].theme_name);
      });
  }, [id]);

  return (
    <div style={{ padding: '2rem' }}>
      <h2>테마 상세 페이지: {themeName} (ID: {id})</h2>
      <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: 16 }}>
        <thead>
          <tr>
            <th>티커</th>
            <th>종목명</th>
            <th>현재가</th>
            <th>전일대비</th>
            <th>등락률</th>
            <th>거래량</th>
            <th>거래대금</th>
            <th>전일거래량</th>
            <th>비고</th>
          </tr>
        </thead>
        <tbody>
          {stocks.map(stock => (
            <tr key={stock.stock_id}>
              <td>{stock.ticker}</td>
              <td>{stock.name}</td>
              <td>{stock.current_price ?? '-'}</td>
              <td>{stock.diff_price ?? '-'}</td>
              <td style={{ color: stock.change_rate && stock.change_rate > 0 ? '#d32f2f' : stock.change_rate && stock.change_rate < 0 ? '#1976d2' : '#333' }}>
                {stock.change_rate !== undefined ? (stock.change_rate > 0 ? '+' : '') + (stock.change_rate * 100).toFixed(2) + '%' : '-'}
              </td>
              <td>{stock.volume ?? '-'}</td>
              <td>{stock.trading_value ?? '-'}</td>
              <td>{stock.volume_yesterday ?? '-'}</td>
              <td>{stock.description ?? '-'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default ThemeDetail; 