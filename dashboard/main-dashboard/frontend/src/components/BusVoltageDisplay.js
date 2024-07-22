// src/components/BusVoltageDisplay.js
// TODO: Battery percentages for easier interpability

import React, { useState, useEffect } from 'react';

const BusVoltageDisplay = ({ socketData }) => {
  const [busVoltage, setBusVoltage] = useState(null);

  useEffect(() => {
    if (socketData) {
        setBusVoltage(socketData.bus_voltage)
    }
  }, [socketData]);

  return (
    <div>
      <h3>Bus Voltage</h3>
      {busVoltage !== null ? <p>{busVoltage} V</p> : <p>Loading...</p>}
      {busVoltage < 22.5 ? <p>Bus Voltage Low, Charge Now</p> : <p>Bus Voltage </p>}
    </div>
  );
};

export default BusVoltageDisplay;
