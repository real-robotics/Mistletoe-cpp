// src/App.js
import React, { useEffect, useState } from 'react';
import Graph from './components/Graph';
import ToggleButton from './components/ToggleButton';
import BusVoltageDisplay from './components/BusVoltageDisplay';
import FaultMessage from './components/FaultDisplay';
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
    <div>
      <Graph socketData={socketData}/>
      <ToggleButton socket={socket} socketData={socketData}/>
      <BusVoltageDisplay socketData={socketData}/>
      <FaultMessage socketData={socketData}/>
    </div>
  );
};

export default App;
