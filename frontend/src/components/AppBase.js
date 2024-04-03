/* App Landing Page. */
import * as React from 'react';
import { Box } from "@mui/material";
import { createTheme, ThemeProvider } from '@mui/material/styles';
import { getDesignTokens, getSavedThemeMode, setSavedThemeMode } from "../theme";
import CssBaseline from '@mui/material/CssBaseline';
import AdminAppBar from './AdminAppBar';
import { Toaster } from 'react-hot-toast';
import AdminAppDrawer from './AdminAppDrawer';
import { api_client, fetchToken } from '../auth';

const drawerWidth = 220;

export default function AppBase({bannerTitle, children}) {
  const [myAccount, setMyAccount] = React.useState(null);
  const [pageLoadComplete, setPageLoadComplete] = React.useState(false);
  const [mode, setMode] = React.useState(getSavedThemeMode());
  const [theme, setTheme] = React.useState(createTheme(getDesignTokens(mode)));

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
      var defaultTheme = getSavedThemeMode();
      if (defaultTheme === null){
        defaultTheme = (themePreference ? 'dark' : 'light');
        setSavedThemeMode(defaultTheme);
      }
      setMode(defaultTheme);
      document.documentElement.setAttribute('data-color-mode', defaultTheme);
      setTheme(createTheme(getDesignTokens(defaultTheme)));
      setPageLoadComplete(true);
    }
  }

  // Theme Changer Function
  const toggleThemeSetting = () => {
    var newTheme = (mode === 'light' ? 'dark' : 'light');
    setSavedThemeMode(newTheme);
    setMode(newTheme);
    setTheme(createTheme(getDesignTokens(newTheme)));
  }

  return (
    <ThemeProvider theme={theme}>
      <Box sx={{ display: 'flex' }}>
        <CssBaseline />
        <div className="AppBase">
          <Toaster
            position="bottom-right"
            reverseOrder={false}
          />
          <Box sx={{ display: 'flex' }}>
            <AdminAppBar
                title={bannerTitle}
                mode={mode}
                onLoad={setDefaultTheme}
                onThemeChange={toggleThemeSetting}
            />
            <AdminAppDrawer drawerWidth={drawerWidth} account={myAccount}>
              {children}
            </AdminAppDrawer>
          </Box>
        </div>
      </Box>
    </ThemeProvider>
  );
}
