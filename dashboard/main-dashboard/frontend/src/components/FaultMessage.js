// src/components/FaultMessage.js

import React, { useState, useEffect } from 'react';
import { Typography, Box } from '@mui/material';

const FaultMessage = ({ socketData }) => {
  const [faultCode, setFaultCode] = useState(null);

  useEffect(() => {
    if (socketData && socketData.fault_code !== undefined) {
      setFaultCode(socketData.fault_code);
    }
  }, [socketData]);

  return (
    <Box textAlign="left" p={2}>
      {faultCode !== null ? (
        <Typography
          variant="body1"
          style={{ color: faultCode !== 0 ? 'red' : 'green', fontWeight: 'bold' }}
        >
          {faultCode !== 0 ? `Fault detected in at least one controller, fault code: ${faultCode}` : 'No faults detected.'}
        </Typography>
      ) : (
        <Typography>Loading...</Typography>
      )}
    </Box>
  );
};

export default FaultMessage;
