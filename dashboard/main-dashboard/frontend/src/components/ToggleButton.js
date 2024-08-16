// src/components/ToggleButton.js

import React, { useState } from 'react';
import { Button, Box, Typography } from '@mui/material';
import { sendWebSocketMessage } from '../utils/websocket';

const ToggleButton = ({ socket, socketData }) => {
  const [isEnabled, setIsEnabled] = useState(false);

  const toggleButton = () => {
    const newStatus = !isEnabled;
    setIsEnabled(newStatus);
    sendWebSocketMessage(socket, { enabled: newStatus });
  };

  return (
    <Box textAlign="left" p={2}>
      <Typography variant="h6" color="textPrimary" sx={{ marginBottom: 1 }}>
        Enabled Status:
      </Typography>
      <Button
        onClick={toggleButton}
        variant="contained"
        color={isEnabled ? 'success' : 'error'}
        fullWidth
      >
        {isEnabled ? 'Enabled' : 'Disabled'}
      </Button>
    </Box>
  );
};

export default ToggleButton;
