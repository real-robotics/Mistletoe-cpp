import React, { useEffect, useState } from 'react';
import MainContainer from './MainContainer';
import { connectWebSocket } from './utils/websocket';
import './styles.css';

const App = () => {
  const [socket, setSocket] = useState(null);
  const [socketData, setSocketData] = useState(null);

  useEffect(() => {
    const socketConnection = connectWebSocket('ws://localhost:8080', (data) => {
      setSocketData(data);
    });
    setSocket(socketConnection);
  }, []);

  return <MainContainer socketData={socketData} socket={socket} />;
};

export default App;
