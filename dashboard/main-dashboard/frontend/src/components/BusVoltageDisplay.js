// src/components/BusVoltageDisplay.js

import React, { useState, useEffect } from 'react';
import { voltageToPercentage } from '../utils/voltageUtils';

const BusVoltageDisplay = ({ socketData }) => {
  const [busVoltage, setBusVoltage] = useState(null);

  useEffect(() => {
    if (socketData) {
      setBusVoltage(socketData.bus_voltage);
    }
  }, [socketData]);

  const getPercentageColor = (percentage) => {
    if (percentage <= 15) return 'darkred'; // Darker red for better contrast
    if (percentage > 15 && percentage <= 20) return 'orange'; // More readable orange
    if (percentage > 80 && percentage <= 100) return 'orange'; // More readable orange
    if (percentage > 20 && percentage <= 80) return 'green';
    return 'green';
  };

  const truncateVoltage = (voltage) => (Math.round(voltage * 100) / 100).toFixed(2);

  const percentage = busVoltage !== null ? voltageToPercentage(busVoltage) : null;

  return (
    <div>
      <h3 style={{ color: 'black' }}>Bus Voltage</h3>
      {busVoltage !== null ? (
        <div>
          <p style={{ color: getPercentageColor(percentage), fontWeight: 'bold' }}>
            {truncateVoltage(busVoltage)} V ({percentage.toFixed(0)}%)
          </p>
          <p style={{ color: getPercentageColor(percentage), fontWeight: 'bold' }}>
            {percentage < 20 ? 'Bus Voltage Low, Charge Now' : 'Bus Voltage Normal'}
          </p>
        </div>
      ) : (
        <p>Loading...</p>
      )}
    </div>
  );
};

export default BusVoltageDisplay;
