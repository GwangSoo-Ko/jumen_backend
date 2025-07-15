import { BrowserRouter, Routes, Route } from 'react-router-dom';
import ThemeList from './pages/ThemeList';
import ThemeDetail from './pages/ThemeDetail';
import Dashboard from './pages/Dashboard';

function App() {
  return (
    <BrowserRouter>
        <Routes>
          <Route path="/themes" element={<ThemeList />} />
          <Route path="/themes/:id" element={<ThemeDetail />} />
          <Route path="/dashboard" element={<Dashboard />} />
        </Routes>
    </BrowserRouter>
  );
}

export default App;
