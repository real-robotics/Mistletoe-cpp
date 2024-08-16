// src/components/BusVoltageDisplay.js
import React, { useState, useEffect } from 'react';
import { Typography, Box } from '@mui/material';
import { voltageToPercentage } from '../utils/voltageUtils';

const BusVoltageDisplay = ({ socketData }) => {
  const [busVoltage, setBusVoltage] = useState(null);

  useEffect(() => {
    if (socketData) {
      setBusVoltage(socketData.bus_voltage);
    }
  }, [socketData]);

  const getPercentageColor = (percentage) => {
    if (percentage <= 15) return '#ff6b6b';
    if (percentage > 15 && percentage <= 20) return '#ffcc00';
    if (percentage > 80 && percentage <= 100) return '#ffcc00';
    if (percentage > 20 && percentage <= 80) return '#1e88e5';
    return '#1e88e5';
  };

  const truncateVoltage = (voltage) => (Math.round(voltage * 100) / 100).toFixed(2);

  const percentage = busVoltage !== null ? voltageToPercentage(busVoltage) : null;

  return (
    <Box textAlign="left" 
    p={2}
    >
      <Typography variant="h6">Bus Voltage</Typography>
      {busVoltage !== null ? (
        <Box>
          <Typography
            variant="body1"
            style={{ color: getPercentageColor(percentage), fontWeight: 'bold' }}
          >
            {truncateVoltage(busVoltage)} V ({percentage.toFixed(0)}%)
          </Typography>
          <Typography
            variant="body1"
            style={{ color: getPercentageColor(percentage), fontWeight: 'bold' }}
          >
            {percentage < 20 ? 'Bus Voltage Low, Charge Now' : 'Bus Voltage Normal'}
          </Typography>
        </Box>
      ) : (
        <Typography>Loading...</Typography>
      )}
    </Box>
  );
};

export default BusVoltageDisplay;
