import { BrowserRouter, Routes, Route } from 'react-router-dom';
import ThemeList from './pages/ThemeList';
import ThemeDetail from './pages/ThemeDetail';
import SectorList from './pages/SectorList';
import SectorDetail from './pages/SectorDetail';
import OverView from './pages/OverView';
import StrategyBoard from './pages/StrategyBoard';
import FreeBoard from './pages/FreeBoard';
import FreeBoardDetail from './pages/FreeBoardDetail';
import StrategyBoardDetail from './pages/StrategyBoardDetail';
import StrategyBoardEdit from './pages/StrategyBoardEdit';
import FreeBoardWrite from './pages/FreeBoardWrite';
import StrategyBoardWrite from './pages/StrategyBoardWrite';
import SignIn from './pages/SignIn';
import SignUp from './pages/SignUp';
import OAuth2Callback from './pages/OAuth2Callback';
import ProtectedRoute from './components/ProtectedRoute';
import { AuthProvider } from './contexts/AuthContext';

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/* 공개 페이지 */}
          <Route path="/themes" element={<ThemeList />} />
          <Route path="/themes/:id" element={<ThemeDetail />} />
          <Route path="/sectors" element={<SectorList />} />
          <Route path="/sectors/:id" element={<SectorDetail />} />
          <Route path="/overview" element={<OverView />} />
          {/* 인증이 필요한 페이지 */}
          <Route path="/strategy-board" element={
            <ProtectedRoute>
              <StrategyBoard />
            </ProtectedRoute>
          } />
          <Route path="/strategy-board/:id" element={
            <ProtectedRoute>
              <StrategyBoardDetail />
            </ProtectedRoute>
          } />
          <Route path="/strategy-board/edit/:id" element={
            <ProtectedRoute>
              <StrategyBoardEdit />
            </ProtectedRoute>
          } />
          <Route path="/free-board" element={
            <ProtectedRoute>
              <FreeBoard />
            </ProtectedRoute>
          } />
          <Route path="/free-board/:id" element={
            <ProtectedRoute>
              <FreeBoardDetail />
            </ProtectedRoute>
          } />
          <Route path="/strategy-board/write" element={
            <ProtectedRoute>
              <StrategyBoardWrite />
            </ProtectedRoute>
          } />
          <Route path="/free-board/write" element={
            <ProtectedRoute>
              <FreeBoardWrite />
            </ProtectedRoute>
          } />
          
          {/* 인증이 필요하지 않은 페이지 (로그인/회원가입) */}
          <Route path="/sign-in" element={
            <ProtectedRoute requireAuth={false}>
              <SignIn />
            </ProtectedRoute>
          } />
          <Route path="/sign-up" element={
            <ProtectedRoute requireAuth={false}>
              <SignUp />
            </ProtectedRoute>
          } />
          <Route path="/oauth2/callback" element={<OAuth2Callback />} />
          
          {/* 기본 경로 */}
          <Route path="/" element={
            <ProtectedRoute>
              <OverView />
            </ProtectedRoute>
          } />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
