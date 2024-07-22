// src/ToggleButton.js

import React, { useState } from 'react';
import { sendWebSocketMessage } from '../utils/websocket';

const ToggleButton = ({ socket, socketData }) => {
  const [isEnabled, setIsEnabled] = useState(false);

  const toggleButton = () => {
    if (socketData && socketData.fault_code === 0) {
      const newState = !isEnabled;
      setIsEnabled(newState);
      if (socket) {
        sendWebSocketMessage(socket, { type: 'toggleButton', enabled: newState });
      }  
    }
  };

  return (
    <button
      onClick={toggleButton}
      style={{ backgroundColor: isEnabled ? 'green' : 'red', color: 'white' }}
    >
      {isEnabled ? 'Enabled' : 'Disabled'}
    </button>
  );
};

export default ToggleButton;
