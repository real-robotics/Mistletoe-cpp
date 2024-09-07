import React, { useEffect, useState } from 'react';
import { ThemeProvider, CssBaseline } from '@mui/material';
import MainContainer from './MainContainer';
import theme from './theme';
import { connectWebSocket } from './utils/websocket';

const App = () => {
  const [socket, setSocket] = useState(null);
  const [socketData, setSocketData] = useState(null);

  useEffect(() => {
    const socketConnection = connectWebSocket('ws://localhost:8080', (data) => {
      setSocketData(data);
    });
    setSocket(socketConnection);
  }, []);

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <MainContainer socket={socket} socketData={socketData} />
    </ThemeProvider>
  );
};

export default App;