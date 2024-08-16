// src/theme.js
import { createTheme } from '@mui/material/styles';

const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#1e88e5', // Bright blue for primary actions
    },
    secondary: {
      main: '#ff6b6b', // Red for secondary actions or warnings
    },
    background: {
      default: '#0d1117', // Darker background for the overall layout
      paper: '#161b22', // Slightly lighter background for card-like components
    },
    text: {
      primary: '#c9d1d9', // Lighter text for better readability on dark backgrounds
      secondary: '#8b949e', // Dimmer text for less important elements
    },
  },
  typography: {
    fontFamily: 'Inter, Arial, sans-serif', // Change to Inter
    h4: {
      fontWeight: 700,
      letterSpacing: '0.5px',
      color: '#ffffff',
    },
    h6: {
      fontWeight: 600, // Semi-bold for h6
      color: '#c9d1d9',
    },
    body1: {
      color: '#c9d1d9',
    },
    button: {
      textTransform: 'none',
    },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          borderRadius: 8,
        },
      },
    },
  },
});

export default theme;
