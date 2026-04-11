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
import Tooltip from '@mui/material/Tooltip';
import Link from '@mui/material/Link';
import useMediaQuery from '@mui/material/useMediaQuery';
import { useTheme } from '@mui/material/styles';
import FormControl from '@mui/material/FormControl';
import InputLabel from '@mui/material/InputLabel';
import Select from '@mui/material/Select';
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

function stringAvatar(name, theme) {
  // Extract First Letter of Each Word
  const nameComponents = name.split(' ').map((name) => {return name[0];});

  return {
    sx: {
      bgcolor: stringToColor(name),
      color: theme.palette.getContrastText(stringToColor(name)),
    },
    children: nameComponents.join(""),
  };
}

export default function AdminAppBar({
  title,
  themeId,
  themeOptions,
  onLoad,
  onThemeChange,
}) {
  const theme = useTheme();
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

  const handleThemeSelection = (newThemeId) => {
    onThemeChange(newThemeId);
    handleCloseUserMenu();
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
          <Box sx={{ display: { xs: 'flex', md: 'flex' } }}>
            <Box sx={{ flexGrow: 0 }}>
            <Tooltip title="Open settings">
              <IconButton onClick={handleOpenUserMenu} sx={{ p: 0 }}>
                <Avatar {...stringAvatar(`${window.account_name}`, theme)} />
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
              <MenuItem disableRipple sx={{ cursor: 'default', minWidth: 260 }}>
                <FormControl size="small" fullWidth>
                  <InputLabel id="user-theme-select-label">Theme</InputLabel>
                  <Select
                    labelId="user-theme-select-label"
                    id="user-theme-select"
                    value={themeId}
                    label="Theme"
                    onClick={(event) => {event.stopPropagation();}}
                    onChange={(event) => {handleThemeSelection(event.target.value)}}
                  >
                    {themeOptions.map((themeOption) => (
                      <MenuItem key={themeOption.id} value={themeOption.id}>
                        {themeOption.label}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </MenuItem>
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
