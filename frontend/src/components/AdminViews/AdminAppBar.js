/*******************************************************************************
 * AppBar.js
 * 
 * Application bar (header-bar) to provide selection options for the various
 * "things" that should be accessible in the application.
 ******************************************************************************/
import * as React from 'react';
import AppBar from '@mui/material/AppBar';
import Avatar from '@mui/material/Avatar';
import Box from '@mui/material/Box';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import IconButton from '@mui/material/IconButton';
import MenuIcon from '@mui/icons-material/Menu';
import Menu from '@mui/material/Menu';
import MenuItem from '@mui/material/MenuItem';
import Fade from '@mui/material/Fade';
import Brightness4Icon from '@mui/icons-material/Brightness4';
import Brightness7Icon from '@mui/icons-material/Brightness7';
import Tooltip from '@mui/material/Tooltip';
import Link from '@mui/material/Link';
import useMediaQuery from '@mui/material/useMediaQuery';
import { clearToken, logout } from '../../auth';

function stringToColor(string) {
  let hash = 0;
  let i;

  /* eslint-disable no-bitwise */
  for (i = 0; i < string.length; i += 1) {
    hash = string.charCodeAt(i) + ((hash << 5) - hash);
  }

  let color = '#';

  for (i = 0; i < 3; i += 1) {
    const value = (hash >> (i * 8)) & 0xff;
    color += `00${value.toString(16)}`.slice(-2);
  }
  /* eslint-enable no-bitwise */

  return color;
}

function stringAvatar(name) {
  return {
    sx: {
      bgcolor: stringToColor(name),
      color: '#fff',
    },
    children: `${name.split(' ')[0][0]}${name.split(' ')[1][0]}`,
  };
}

export default function AdminAppBar({
  title,
  mode,
  onLoad,
  onThemeChange, // called every time the user clicks the LightDarkSwitch
}) {
  const [anchorEl, setAnchorEl] = React.useState(null);
  const [anchorElUser, setAnchorElUser] = React.useState(null);
  const menuOpen = Boolean(anchorEl);

  // Function to help secure usage of `_blank`
  const openInNewTab = (url) => {
    const newWindow = window.open(url, '_blank', 'noopener,noreferrer')
    if (newWindow) newWindow.opener = null
  }

  const prefersDarkMode = useMediaQuery(
    '(prefers-color-scheme: dark)',
    { noSsr: true }
  );

  React.useEffect(()=>{
    // Load Requisites when page Completes
    onLoad(prefersDarkMode);
  },[prefersDarkMode, onLoad]);

  const handleMenuClick = (event) => {
    setAnchorEl(event.currentTarget);
  };
  const openRepo = () => {
    openInNewTab("https://github.com/engineerjoe440/audi-hose");
    handleMenuClose();
  }
  const handleMenuClose = () => {
    setAnchorEl(null);
  };
  const handleOpenUserMenu = (event) => {
    setAnchorElUser(event.currentTarget);
  };
  const handleCloseUserMenu = () => {
    setAnchorElUser(null);
  };
  
  const handleLogout = () => {
    handleCloseUserMenu();
    logout();
    clearToken();
    window.location.href = "/";
  }

  return (
    <Box sx={{ flexGrow: 1 }}>
      <AppBar position="fixed" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}>
        <Toolbar>
          <IconButton
            id="menu-button"
            size="large"
            edge="start"
            color="inherit"
            aria-label="menu"
            sx={{ mr: 2 }}
            aria-controls={menuOpen ? 'fade-menu' : undefined}
            aria-haspopup="true"
            aria-expanded={menuOpen ? 'true' : undefined}
            onClick={handleMenuClick}
          >
            <MenuIcon />
          </IconButton>
          <Menu
            id="fade-menu"
            MenuListProps={{
              'aria-labelledby': 'fade-button',
            }}
            anchorEl={anchorEl}
            open={menuOpen}
            onClose={handleMenuClose}
            TransitionComponent={Fade}
          >
            <MenuItem onClick={openRepo}>Repository</MenuItem>
          </Menu>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            {window.location.pathname === "/" ?
              <Link href="/" underline="none" color="inherit">
                {title}
              </Link>
            :
              <Link href="/" underline="none" color="inherit">
                {title}
              </Link>
            }
          </Typography>
          <Box sx={{ display: { xs: 'none', md: 'flex' } }}>
            <Tooltip title={mode === 'dark' ? "Light Mode" : "Dark Mode"}>
              <IconButton sx={{ ml: 1 }} onClick={onThemeChange} color="inherit">
                {mode === 'dark' ? <Brightness7Icon /> : <Brightness4Icon />}
              </IconButton>
            </Tooltip>
            <Box sx={{ flexGrow: 0 }}>
            <Tooltip title="Open settings">
              <IconButton onClick={handleOpenUserMenu} sx={{ p: 0 }}>
                <Avatar {...stringAvatar(`${window.account_name}`)} />
              </IconButton>
            </Tooltip>
            <Menu
              sx={{ mt: '45px' }}
              id="menu-appbar"
              anchorEl={anchorElUser}
              anchorOrigin={{
                vertical: 'top',
                horizontal: 'right',
              }}
              keepMounted
              transformOrigin={{
                vertical: 'top',
                horizontal: 'right',
              }}
              open={Boolean(anchorElUser)}
              onClose={handleCloseUserMenu}
            >
              {/* Area for Potential User Settings Link. */}
              {/* <MenuItem
                key="User Settings"
                onClick={() => {window.location.href = "/user-settings"}}
              >
                <Typography textAlign="center">User Settings</Typography>
              </MenuItem> */}
              <MenuItem key="logout" onClick={handleLogout}>
                <Typography textAlign="center">Logout</Typography>
              </MenuItem>
            </Menu>
          </Box>
          </Box>
        </Toolbar>
      </AppBar>
    </Box>
  );
}
