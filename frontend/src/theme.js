/*******************************************************************************
 * theme.js
 * 
 * Theme control file for managing the basic light/dark theme for application.
 ******************************************************************************/

import { green } from '@mui/material/colors';
import { styled } from '@mui/material/styles';
import { Paper } from '@mui/material';


export const PageSection = styled(Paper)(({ theme }) => ({
  backgroundColor: theme.palette.mode === 'dark' ? '#1A2027' : '#fff',
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
             main: green[800],
             text: '#ffffff',
           },
           secondary: {
             main: green[800],
             alt: '#ffffff',
             altTable: "#eaebea",
             text: green[800],
           },
        }
        : {
            // palette values for dark mode
           primary: {
             main: green[800],
             text: '#ffffff',
           },
           secondary: {
             main: "#ffffff",
             alt: green[100],
             altTable: "#3f7c42",
             text: "#000000",
           },
           background: {
              default: '#051700',
              paper: green[800],
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