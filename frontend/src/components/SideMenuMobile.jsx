import * as React from 'react';
import PropTypes from 'prop-types';
import Avatar from '@mui/material/Avatar';
import Button from '@mui/material/Button';
import Divider from '@mui/material/Divider';
import Drawer, { drawerClasses } from '@mui/material/Drawer';
import Stack from '@mui/material/Stack';
import Typography from '@mui/material/Typography';
import LogoutRoundedIcon from '@mui/icons-material/LogoutRounded';
import NotificationsRoundedIcon from '@mui/icons-material/NotificationsRounded';
import MenuButton from './MenuButton';
import MenuContent from './MenuContent';
import CardAlert from './CardAlert';
import { useAuth, fetchWithAuth } from '../contexts/AuthContext';

function SideMenuMobile({ open, toggleDrawer }) {
  const { user, setUser } = useAuth();
  const handleLogout = () => {
    fetchWithAuth('http://localhost:8000/auth/logout', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: localStorage.getItem('refresh_token') })
    });
    setUser(null); // 전역 로그아웃 처리
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    window.location.href = '/overview';
  };
  return (
    <Drawer
      anchor="right"
      open={open}
      onClose={toggleDrawer(false)}
      sx={{
        zIndex: (theme) => theme.zIndex.drawer + 1,
        [`& .${drawerClasses.paper}`]: {
          backgroundImage: 'none',
          backgroundColor: 'background.paper',
        },
      }}
    >
      <Stack
        sx={{
          maxWidth: '70dvw',
          height: '100%',
        }}
      >
        <Stack direction="row" sx={{ p: 2, pb: 0, gap: 1 }}>
          {user ? (
            <Stack direction="row" sx={{ gap: 1, alignItems: 'center', flexGrow: 1, p: 1 }}>
              <Avatar
                sizes="small"
                alt={user.nickname || 'User'}
                src={user.profile_img || '/static/images/avatar/7.jpg'}
                sx={{ width: 24, height: 24 }}
              />
              <Typography component="p" variant="h6">
                {user.nickname}
              </Typography>
            </Stack>
          ) : (
            <Stack direction="row" sx={{ gap: 1, alignItems: 'center', flexGrow: 1, p: 1 }}>
              <Avatar sizes="small" sx={{ width: 24, height: 24 }} />
              <Typography component="p" variant="h6">
                로그인 필요
              </Typography>
            </Stack>
          )}
          {/* <MenuButton showBadge>
            <NotificationsRoundedIcon />
          </MenuButton> */}
        </Stack>
        <Divider />
        <Stack sx={{ flexGrow: 1 }}>
          <MenuContent />
          <Divider />
        </Stack>
        {/* <CardAlert /> */}
        <Stack sx={{ p: 2 }}>
          {user ? (
            <Button
              variant="outlined"
              fullWidth
              startIcon={<LogoutRoundedIcon />}
              onClick={handleLogout}
            >
              로그아웃
            </Button>
          ) : (
            <>
              <Button variant="outlined" fullWidth href="/sign-in" sx={{ mb: 1 }}>
                로그인
              </Button>
              <Button variant="contained" fullWidth href="/sign-up">
                회원가입
              </Button>
            </>
          )}
        </Stack>
      </Stack>
    </Drawer>
  );
}

SideMenuMobile.propTypes = {
  open: PropTypes.bool,
  toggleDrawer: PropTypes.func.isRequired,
};

export default SideMenuMobile;
