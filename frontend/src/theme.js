/*******************************************************************************
 * theme.js
 *
 * Theme control file for managing the basic light/dark theme for application.
 ******************************************************************************/

import { styled } from '@mui/material/styles';
import { Paper } from '@mui/material';


export const PageSection = styled(Paper)(({ theme }) => ({
  backgroundColor: theme.palette.background.paper,
  ...theme.typography.body2,
  padding: theme.spacing(1),
  textAlign: 'center',
  color: theme.palette.text.primary,
}));


const themeKey = "audi-hose-theme";

const themeDefinitions = {
  studioNight: {
    label: 'Studio Night',
    mode: 'dark',
    palette: {
      primary: { main: '#145A75', text: '#FFFFFF' },
      secondary: { main: '#FF5A1F', alt: '#0E2D42', altTable: '#123A4F', text: '#F6B24D' },
      background: { default: '#081826', paper: '#0E2D42' },
    },
  },
  onAirContrast: {
    label: 'On-Air Contrast',
    mode: 'dark',
    palette: {
      primary: { main: '#1EA7C9', text: '#0A0F1A' },
      secondary: { main: '#FF4B1F', alt: '#123247', altTable: '#1A3F57', text: '#D9DEE5' },
      background: { default: '#0A0F1A', paper: '#123247' },
    },
  },
  cinematicTech: {
    label: 'Cinematic Tech',
    mode: 'dark',
    palette: {
      primary: { main: '#1B6F8C', text: '#FFFFFF' },
      secondary: { main: '#FF6A2A', alt: '#0F3A52', altTable: '#194A63', text: '#BFC9D4' },
      background: { default: '#06131F', paper: '#0F3A52' },
    },
  },
  warmBroadcast: {
    label: 'Warm Broadcast',
    mode: 'light',
    palette: {
      primary: { main: '#1C3D52', text: '#FFFFFF' },
      secondary: { main: '#FF5E2E', alt: '#2A7FA1', altTable: '#DDE8EE', text: '#101820' },
      background: { default: '#FFD07A', paper: '#FFFFFF' },
    },
  },
  minimalDarkUi: {
    label: 'Minimal Dark UI',
    mode: 'dark',
    palette: {
      primary: { main: '#1F9BBF', text: '#E8EEF4' },
      secondary: { main: '#FF5522', alt: '#162B3A', altTable: '#1D3548', text: '#E8EEF4' },
      background: { default: '#0B1220', paper: '#162B3A' },
    },
  },
  afterhoursGlow: {
    label: 'Afterhours Glow',
    mode: 'dark',
    palette: {
      primary: { main: '#0AB1C9', text: '#142734' },
      secondary: { main: '#C4724F', alt: '#106682', altTable: '#0B8BA9', text: '#EAF7FA' },
      background: { default: '#142734', paper: '#106682' },
    },
  },
  colorful: {
    label: 'Colorful',
    mode: 'dark',
    palette: {
      primary: { main: '#04ADBF', text: '#032F40' },
      secondary: { main: '#F23C13', alt: '#04D9D9', altTable: '#401111', text: '#F5FAFA' },
      background: { default: '#032F40', paper: '#401111' },
    },
  },
  deepSounds: {
    label: 'Deep Sounds',
    mode: 'dark',
    palette: {
      primary: { main: '#04ADBF', text: '#032F40' },
      secondary: { main: '#730C02', alt: '#035E73', altTable: '#401111', text: '#E6F7FA' },
      background: { default: '#032F40', paper: '#035E73' },
    },
  },
};

export const DEFAULT_THEME_ID = 'studioNight';

export const THEME_OPTIONS = Object.entries(themeDefinitions).map(([id, config]) => ({
  id,
  label: config.label,
}));

function resolveThemeId(themeId, fallbackThemeId = DEFAULT_THEME_ID) {
  if (themeDefinitions[themeId]) {
    return themeId;
  }

  // Backward compatibility with the historical light/dark toggle.
  if (themeId === 'dark') {
    return 'studioNight';
  }
  if (themeId === 'light') {
    return 'warmBroadcast';
  }

  return fallbackThemeId;
}

export const getDesignTokens = (themeId) => {
  const selectedThemeId = resolveThemeId(themeId);
  const selectedTheme = themeDefinitions[selectedThemeId];

  return {
    palette: {
      mode: selectedTheme.mode,
      ...selectedTheme.palette,
    },
  };
};

// Define Functions to Store and Retrieve Theme
export function getSavedThemeMode(fallbackThemeId = DEFAULT_THEME_ID) {
    const storedThemeId = localStorage.getItem(themeKey);
    return resolveThemeId(storedThemeId, fallbackThemeId);
}
export function setSavedThemeMode(themeId) {
    localStorage.setItem(themeKey, resolveThemeId(themeId));
}
