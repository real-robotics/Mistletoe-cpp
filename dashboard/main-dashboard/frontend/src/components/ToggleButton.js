// src/ToggleButton.js
import React, { useState } from 'react';
import { sendWebSocketMessage } from './websocket';

const ToggleButton = ({ socket }) => {
  const [isEnabled, setIsEnabled] = useState(false);

  const toggleButton = () => {
    const newState = !isEnabled;
    setIsEnabled(newState);
    if (socket) {
      sendWebSocketMessage(socket, { type: 'toggleButton', enabled: newState });
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
