/* GrantSplat Landing Page. */
import * as React from 'react';
import { Box } from "@mui/material";
import { createTheme, ThemeProvider } from '@mui/material/styles';
import { getDesignTokens, getSavedThemeMode, setSavedThemeMode } from "./theme";
import CssBaseline from '@mui/material/CssBaseline';
import AdminAppBar from './components/AdminAppBar';
import { Toaster } from 'react-hot-toast';

export default function GrantSplatApp({bannerTitle, children}) {
  const [pageLoadComplete, setPageLoadComplete] = React.useState(false);
  const [mode, setMode] = React.useState(getSavedThemeMode());
  const [theme, setTheme] = React.useState(createTheme(getDesignTokens(mode)));

  React.useEffect(()=>{
    // Load Requisites when page Completes
  },[]);

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
      <CssBaseline />
      <div className="Audi-Hose-App">
        <Toaster
          position="bottom-right"
          reverseOrder={false}
        />
        <AdminAppBar
            title={bannerTitle}
            mode={mode}
            onLoad={setDefaultTheme}
            onThemeChange={toggleThemeSetting}
        />
        <Box m={2} sx={{ flexGrow: 1 }}>
          {children}
        </Box>
      </div>
    </ThemeProvider>
  );
}

