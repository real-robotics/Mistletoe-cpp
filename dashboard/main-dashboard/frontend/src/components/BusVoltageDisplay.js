import React, { useState, useEffect } from 'react';

const BusVoltageDisplay = ({ socketData }) => {
  const [busVoltage, setBusVoltage] = useState(null);

  useEffect(() => {
    if (socketData) {
      setBusVoltage(socketData.bus_voltage);
    }
  }, [socketData]);


  const getPercentageColor = (percentage) => {
    if (percentage >= 80) return 'green';
    if (percentage >= 40) return 'yellow';
    return 'red';
  };

  const truncateVoltage = (voltage) => (Math.round(voltage * 100) / 100).toFixed(2);

  return (
    <div>
      <h3 style={{ color: 'black' }}>Bus Voltage</h3>
      {busVoltage !== null ? (
        <div>
          <p style={{ color: getPercentageColor(busVoltage) }}>
            {truncateVoltage(busVoltage)} V ({0}%)
          </p>
          <p style={{ color: getPercentageColor((busVoltage))}}>
            {busVoltage < 22.5 ? 'Bus Voltage Low, Charge Now' : 'Bus Voltage Normal'}
          </p>
        </div>
      ) : (
        <p>Loading...</p>
      )}
    </div>
  );
};

export default BusVoltageDisplay;
