import React from 'react';
import { Link } from 'react-router-dom';

const SiteLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <div style={{ minHeight: '100vh', background: '#f5f7fa' }}>
    <header style={{ background: '#1976d2', padding: '1rem 2rem', color: '#fff', marginBottom: 32 }}>
      <nav style={{ display: 'flex', alignItems: 'center', gap: 24 }}>
        <Link to="/" style={{ color: '#fff', fontWeight: 700, fontSize: 22, textDecoration: 'none' }}>
          JUMEN STOCK
        </Link>
        <Link to="/themes" style={{ color: '#fff', fontWeight: 500, fontSize: 18, textDecoration: 'none' }}>
          테마(섹터) 목록
        </Link>
      </nav>
    </header>
    <main style={{ maxWidth: 1200, margin: '0 auto' }}>{children}</main>
  </div>
);

export default SiteLayout; 