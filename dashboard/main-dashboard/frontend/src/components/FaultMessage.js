import React, { useState, useEffect } from 'react';

const FaultMessage = ({ socketData }) => {
  const [faultCode, setFaultCode] = useState(null);

  useEffect(() => {
    if (socketData && socketData.fault_code !== undefined) {
      setFaultCode(socketData.fault_code);
    }
  }, [socketData]);

  return (
    <div>
      {faultCode !== null ? (
        <p style={{ color: faultCode !== 0 ? 'red' : 'green' }}>
          {faultCode !== 0 ? `Fault detected, fault code: ${faultCode}` : 'No faults detected.'}
        </p>
      ) : (
        <p>Loading...</p>
      )}
    </div>
  );
};

export default FaultMessage;
