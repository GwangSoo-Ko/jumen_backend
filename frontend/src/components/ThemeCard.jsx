import React from 'react';
import Button from '@mui/material/Button';
import Tooltip from '@mui/material/Tooltip';


const getRateColor = (rate) => (rate > 0 ? '#d32f2f' : rate < 0 ? '#1976d2' : '#333');

const ThemeCard = ({ name, change_rate, avg_change_rate_3days, up_ticker_count, neutral_ticker_count, down_ticker_count, companyCount, onClick }) => (
  <div
    className="theme-card"
    onClick={onClick}
    style={{
      border: '1px solid #e0e0e0',
      borderRadius: 12,
      padding: 24,
      margin: 12,
      width: 280,
      background: '#fff',
      boxShadow: '0 2px 8px rgba(0,0,0,0.07)',
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'space-between',
      cursor: 'pointer',
      transition: 'box-shadow 0.2s, transform 0.2s',
    }}
    onMouseOver={e => {
      e.currentTarget.style.boxShadow = '0 4px 16px rgba(25,118,210,0.15)';
      e.currentTarget.style.transform = 'translateY(-4px) scale(1.03)';
    }}
    onMouseOut={e => {
      e.currentTarget.style.boxShadow = '0 2px 8px rgba(0,0,0,0.07)';
      e.currentTarget.style.transform = 'none';
    }}
  >
    <div>   
    <Tooltip title={name} placement="top-start">
  <h3
    style={{
      margin: '0 0 8px 0',
      color: '#1976d2',
      fontWeight: 700,
      fontSize: 20,
      whiteSpace: 'nowrap',
      overflow: 'hidden',
      textOverflow: 'ellipsis',
    }}
  >
    {name}
  </h3>
</Tooltip>
      {/* <h3 style={{ margin: '0 0 8px 0', color: '#1976d2', fontWeight: 700 }}>{name}</h3> */}
      <p style={{ fontWeight: 500, margin: 0, color: '#333' }}>
        등락률: <span style={{ color: getRateColor(change_rate) }}>
          {change_rate > 0 ? '+' : ''}{(change_rate * 100).toFixed(2)}%
        </span>
      </p>
      <p style={{ margin: '2px 0 0 0', fontWeight: 500, color: '#333' }}>
        3일평균 등락률: <span style={{ color: getRateColor(avg_change_rate_3days) }}>
          {avg_change_rate_3days > 0 ? '+' : ''}{(avg_change_rate_3days * 100).toFixed(2)}%
        </span>
      </p>
      <p style={{ fontWeight: 500, margin: 0, color: '#333' }}>상승 종목 수: <span style={{ color: '#d32f2f' }}>{up_ticker_count}</span></p>
      <p style={{ fontWeight: 500, margin: 0, color: '#333' }}>중립 종목 수: <span style={{ color: '#333' }}>{neutral_ticker_count}</span></p>
      <p style={{ fontWeight: 500, margin: 0, color: '#333' }}>하락 종목 수: <span style={{ color: '#1976d2' }}>{down_ticker_count}</span></p>
      <p style={{ fontWeight: 500, margin: 0, color: '#333' }}>전체 종목 수: <span style={{ color: '#333' }}>{companyCount}</span></p>
    </div>
    <Button
      style={{
        marginTop: 18,
        padding: '8px 0',
        borderRadius: 8,
        border: 'none',
        background: '#1976d2',
        color: '#fff',
        fontWeight: 600,
        cursor: 'pointer',
        width: '100%',
        fontSize: 15,
        letterSpacing: 1,
      }}
      onClick={e => {
        e.stopPropagation();
        onClick();
      }}
    >
      상세보기
    </Button>
  </div>
);

export default ThemeCard; 
