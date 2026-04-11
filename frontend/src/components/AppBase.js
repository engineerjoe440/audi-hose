/* App Landing Page. */
import * as React from 'react';
import { Box } from "@mui/material";
import { createTheme, ThemeProvider } from '@mui/material/styles';
import { THEME_OPTIONS, getDesignTokens, getSavedThemeMode, setSavedThemeMode } from "../theme";
import CssBaseline from '@mui/material/CssBaseline';
import AdminAppBar from './AdminViews/AdminAppBar';
import AdminAppDrawer from './AdminViews/AdminAppDrawer';
import { api_client, fetchToken } from '../auth';

const drawerWidth = 220;

export default function AppBase({bannerTitle, onNavigate, children}) {
  const [myAccount, setMyAccount] = React.useState(null);
  const [pageLoadComplete, setPageLoadComplete] = React.useState(false);
  const [themeId, setThemeId] = React.useState(getSavedThemeMode());
  const [theme, setTheme] = React.useState(createTheme(getDesignTokens(themeId)));

  React.useEffect(()=>{
    // Load Requisites when page Completes
    getAccount();
  },[]);

  const getAccount = () => {
    api_client.get("accounts/me", {
      withCredentials: true,
      headers: {
        'Accept': 'application/json',
        'Authorization': `Bearer ${fetchToken()}`
      },
    }).then(res => res.data).then(jsonData => {
      // Record the Active Account
      setMyAccount(jsonData);
    })
    .catch((error) => {
      if( error.response ){
        console.log(error.response.data); // => the response payload
      }
    });
  }

  // Theme Default Setter
  const setDefaultTheme = (themePreference) => {
    // Set the default color profile - only if we haven't done so before!
    if (!pageLoadComplete) {
      const fallbackThemeId = (themePreference ? 'studioNight' : 'warmBroadcast');
      const defaultThemeId = getSavedThemeMode(fallbackThemeId);

      setSavedThemeMode(defaultThemeId);
      setThemeId(defaultThemeId);
      document.documentElement.setAttribute(
        'data-color-mode',
        createTheme(getDesignTokens(defaultThemeId)).palette.mode
      );
      setTheme(createTheme(getDesignTokens(defaultThemeId)));
      setPageLoadComplete(true);
    }
  }

  // Theme Changer Function
  const setThemeSetting = (newThemeId) => {
    setSavedThemeMode(newThemeId);
    setThemeId(newThemeId);
    document.documentElement.setAttribute(
      'data-color-mode',
      createTheme(getDesignTokens(newThemeId)).palette.mode
    );
    setTheme(createTheme(getDesignTokens(newThemeId)));
  }

  return (
    <ThemeProvider theme={theme}>
      <Box sx={{ display: 'flex' }}>
        <CssBaseline />
        <Box sx={{ display: 'flex', flexDirection: 'column', flexGrow: 1, minWidth: 0 }}>
          <Box sx={{ display: 'flex', flexGrow: 1, minWidth: 0 }}>
            <AdminAppBar
                title={bannerTitle}
              themeId={themeId}
              themeOptions={THEME_OPTIONS}
                onLoad={setDefaultTheme}
              onThemeChange={setThemeSetting}
            />
            <AdminAppDrawer
              drawerWidth={drawerWidth}
              account={myAccount}
              onNavigate={onNavigate}
            >
              {children}
            </AdminAppDrawer>
          </Box>
        </Box>
      </Box>
    </ThemeProvider>
  );
}
