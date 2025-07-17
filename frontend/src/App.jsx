import { BrowserRouter, Routes, Route } from 'react-router-dom';
import ThemeList from './pages/ThemeList';
import ThemeDetail from './pages/ThemeDetail';
import OverView from './pages/OverView';
import StrategyBoard from './pages/StrategyBoard';
import FreeBoard from './pages/FreeBoard';
import FreeBoardDetail from './pages/FreeBoardDetail';
import StrategyBoardDetail from './pages/StrategyBoardDetail';
import FreeBoardWrite from './pages/FreeBoardWrite';
import StrategyBoardWrite from './pages/StrategyBoardWrite';
import SignIn from './pages/SignIn';
import SignUp from './pages/SignUp';
import OAuth2Callback from './pages/OAuth2Callback';
import { AuthProvider } from './contexts/AuthContext';


function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/themes" element={<ThemeList />} />
          <Route path="/themes/:id" element={<ThemeDetail />} />
          <Route path="/overview" element={<OverView />} />
          <Route path="/strategy-board" element={<StrategyBoard />} />
          <Route path="/strategy-board/:id" element={<StrategyBoardDetail />} />
          <Route path="/free-board" element={<FreeBoard />} />
          <Route path="/free-board/:id" element={<FreeBoardDetail />} />
          <Route path="/strategy-board/write" element={<StrategyBoardWrite />} />
          <Route path="/free-board/write" element={<FreeBoardWrite />} />
          <Route path="/sign-in" element={<SignIn />} />
          <Route path="/sign-up" element={<SignUp />} />
          <Route path="/oauth2/callback" element={<OAuth2Callback />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
