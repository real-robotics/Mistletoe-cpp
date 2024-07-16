import React, { useEffect, useState } from 'react';
import io from 'socket.io-client';
import { Line } from 'react-chartjs-2';
import 'chartjs-adapter-moment';

import { CategoryScale, LinearScale, Chart, PointElement, LineElement } from "chart.js";

Chart.register(CategoryScale, LinearScale, PointElement, LineElement);

const socket = io('http://localhost:4000'); // Your WebSocket server URL

const Dashboard = () => {
  const [data, setData] = useState({
    positions: [],
    velocities: [],
    voltages: [],
  });
  const [selectedJoint, setSelectedJoint] = useState(null);
  const [showWarning, setShowWarning] = useState(false);

  useEffect(() => {
    socket.on('robot-data', (newData) => {
      setData((prevData) => ({
        positions: [...prevData.positions, newData.position],
        velocities: [...prevData.velocities, newData.velocity],
        voltages: [...prevData.voltages, newData.voltage],
      }));
      if (newData.voltage > 10) { // Set your voltage threshold here
        setShowWarning(true);
      }
    });

    return () => {
      socket.off('robot-data');
    };
  }, []);

  const handleShutdown = () => {
    fetch('http://localhost:4000/shutdown', { method: 'POST' }) // Your backend shutdown URL
      .then(response => response.json())
      .then(data => console.log(data));
  };

  const jointOptions = ['Joint 1', 'Joint 2', 'Joint 3', 'Joint 4']; // Add more joints as needed

  const chartData = {
    labels: Array.from({ length: data.positions.length }, (_, i) => i + 1),
    datasets: [
      {
        label: 'Position',
        data: data.positions.map(d => d[selectedJoint]),
        borderColor: 'rgba(75,192,192,1)',
        fill: false,
      },
      {
        label: 'Velocity',
        data: data.velocities.map(d => d[selectedJoint]),
        borderColor: 'rgba(153,102,255,1)',
        fill: false,
      },
      {
        label: 'Voltage',
        data: data.voltages.map(d => d[selectedJoint]),
        borderColor: 'rgba(255,99,132,1)',
        fill: false,
      },
    ],
  };

  const options = {
    scales: {
      x: {
        type: 'category', // Use category scale for categorical labels
        labels: jointOptions,
      },
      y: {
        beginAtZero: true, // Adjust as needed
      },
    },
  };

  return (
    <div>
      <h1>Quadruped Robot Dashboard</h1>
      {showWarning && <div style={{ color: 'red' }}>Warning: High Voltage!</div>}
      <div>
        <label>Select Joint: </label>
        <select onChange={(e) => setSelectedJoint(e.target.value)}>
          <option value="">Select...</option>
          {jointOptions.map((joint, index) => (
            <option key={index} value={index}>{joint}</option>
          ))}
        </select>
      </div>
      {selectedJoint !== null && (
        <div>
          <Line data={chartData} options={options} />
        </div>
      )}
      <button onClick={handleShutdown}>Shutdown</button>
    </div>
  );
};

export default Dashboard;