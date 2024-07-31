import React, { useState } from 'react';
import { sendWebSocketMessage } from '../utils/websocket';

const ToggleButton = ({ socket, socketData }) => {
  const [isEnabled, setIsEnabled] = useState(false);

  const toggleButton = () => {
    const newStatus = !isEnabled;
    setIsEnabled(newStatus);
    sendWebSocketMessage(socket, { enabled: newStatus });
  };

  return (
    <button
      onClick={toggleButton}
      style={{
        backgroundColor: isEnabled ? 'green' : 'red',
        color: 'white',
      }}
      className="button"
    >
      {isEnabled ? 'Enabled' : 'Disabled'}
    </button>
  );
};

export default ToggleButton;
