import { BrowserRouter, Routes, Route } from 'react-router-dom';
import ThemeList from './dashboard/ThemeList';
import ThemeDetail from './dashboard/ThemeDetail';
import Dashboard from './dashboard/Dashboard';

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
