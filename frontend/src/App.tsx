import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Home from './pages/Home';
import ThemeList from './pages/ThemeList';
import ThemeDetail from './pages/ThemeDetail';
import SiteLayout from './components/SiteLayout';

function App() {
  return (
    <BrowserRouter>
      <SiteLayout>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/themes" element={<ThemeList />} />
          <Route path="/themes/:id" element={<ThemeDetail />} />
        </Routes>
      </SiteLayout>
    </BrowserRouter>
  );
}

export default App;
