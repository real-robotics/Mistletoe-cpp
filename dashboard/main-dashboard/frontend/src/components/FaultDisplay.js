import React, { useState, useEffect } from 'react';

const FaultMessage = ({ socketData }) => {
  const [faultCode, setFaultCode] = useState(null);

  useEffect(() => {
    if (socketData && socketData.fault_code) {
      setFaultCode(socketData.fault_code);
    }
  }, [socketData]);

  return (
    <div>
      {faultCode !== null ? (
        <p>Fault detected, fault code: {faultCode}</p>
      ) : (
        <p>No faults detected.</p>
      )}
    </div>
  );
};

export default FaultMessage;
