// src/App.js
import React, { useEffect, useState } from 'react';
import Graph from './components/Graph';
import ToggleButton from './components/ToggleButton';
import { connectWebSocket } from './components/websocket';

const App = () => {
  const [socket, setSocket] = useState(null);

  useEffect(() => {
    const socketConnection = connectWebSocket('ws://localhost:8080', (data) => {
      // Handle incoming messages and update the Graph component as needed
    });
    setSocket(socketConnection);
  }, []);

  return (
    <div>
      <Graph socket={socket} />
      <ToggleButton socket={socket} />
    </div>
  );
};

export default App;
