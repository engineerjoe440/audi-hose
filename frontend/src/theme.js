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
      primary: {
        main: '#1FB8E0',      // brighter cyan for stronger contrast
        text: '#00040A'       // near‑black for maximum readability
      },
      secondary: {
        main: '#FF3A00',      // deeper, more contrast‑stable orange/red
        alt: '#0E2A3A',       // darker blue‑black for UI chrome
        altTable: '#15445C',  // boosted contrast for table backgrounds
        text: '#F2F6FA'       // very light gray for consistent legibility
      },
      background: {
        default: '#00040A',   // true dark for high contrast
        paper: '#0E2A3A'      // slightly lighter but still contrast‑safe
      },
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
      primary: { main: '#9a8661', text: '#FFFFFF' },
      secondary: { main: '#a2553e', alt: '#DAA06D', altTable: '#ede8e1', text: '#6E260E' },
      background: { default: '#cbbca0', paper: '#FFFFFF' },
    },
  },
  afterhoursGlow: {
    label: 'Afterhours Glow',
    mode: 'dark',
    palette: {
      primary: {
        main: '#7AF28A',      // soft terminal‑green glow
        text: '#0F1A17'       // deep green‑black for contrast
      },
      secondary: {
        main: '#4FAF6F',      // muted green accent
        alt: '#1F3A32',       // darker teal‑green for UI chrome
        altTable: '#2C5A45',  // subtle table highlight
        text: '#D8F5E0'       // pale greenish text for readability
      },
      background: {
        default: '#0A0F0A',   // near‑black with a green tint
        paper: '#112018'      // slightly lighter panel background
      },
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
