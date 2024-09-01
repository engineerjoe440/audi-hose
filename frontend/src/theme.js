/*******************************************************************************
 * theme.js
 * 
 * Theme control file for managing the basic light/dark theme for application.
 ******************************************************************************/

import { styled } from '@mui/material/styles';
import { Paper } from '@mui/material';


export const PageSection = styled(Paper)(({ theme }) => ({
  backgroundColor: theme.palette.mode === 'dark' ? '#011E2A' : '#d7f3ff',
  ...theme.typography.body2,
  padding: theme.spacing(1),
  textAlign: 'center',
  color: theme.palette.text.secondary,
}));


const themeKey = "audi-hose-theme";

export const getDesignTokens = (mode) => ({
    palette: {
      mode,
      ...mode === 'light'
        ? {
            // palette values for light mode
           primary: {
             main: '#015C68',
             text: '#FFFFFF',
           },
           secondary: {
             main: '#015C68',
             alt: '#d7f3ff',
             altTable: "#eaebea",
             text: '#d7f3ff',
           },
           background: {
              default: '#d7f3ff',
              paper: '#015C68',
            },
        }
        : {
            // palette values for dark mode
           primary: {
             main: '#5edaf0',
             text: '#ffffff',
           },
           secondary: {
             main: "#ffffff",
             alt: '#d7f3ff',
             altTable: "#3f7c42",
             text: "#ffffff",
           },
           background: {
              default: '#011E2A',
              paper: '#015C68',
            },
        },
    },
  });

// Define Functions to Store and Retrieve Theme
export function getSavedThemeMode() {
    var themeMode = localStorage.getItem(themeKey);
    if (themeMode === 'dark') {
        return 'dark';
    } else {
        return 'light';
    }
}
export function setSavedThemeMode(themeMode) {
    localStorage.setItem(themeKey, themeMode)
}