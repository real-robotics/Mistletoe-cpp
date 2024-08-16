// src/App.js
import React from 'react';
import { ThemeProvider, CssBaseline } from '@mui/material';
import MainContainer from './MainContainer';
import theme from './theme';

const App = () => {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <MainContainer />
    </ThemeProvider>
  );
};

export default App;
