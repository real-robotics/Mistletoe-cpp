// src/Graph.js
import React, { useEffect, useState } from 'react';
import { Line } from 'react-chartjs-2';
import { Chart, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, TimeScale } from 'chart.js';
import 'chartjs-adapter-date-fns';
import { connectWebSocket } from './websocket';

Chart.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, TimeScale);

const Graph = () => {
  const [data, setData] = useState({
    labels: [],
    datasets: [
      {
        label: 'Position',
        data: [],
        borderColor: 'rgba(75, 192, 192, 1)',
        backgroundColor: 'rgba(75, 192, 192, 0.2)',
      },
      {
        label: 'Voltage',
        data: [],
        borderColor: 'rgba(192, 75, 75, 1)',
        backgroundColor: 'rgba(192, 75, 75, 0.2)',
      },
    ],
  });

  useEffect(() => {
    const socket = connectWebSocket('ws://localhost:8080', (newData) => {
      setData((prevData) => {
        const newLabels = [...prevData.labels, newData.timestamp];
        const newPositionData = [...prevData.datasets[0].data, newData.position];
        const newVoltageData = [...prevData.datasets[1].data, newData.voltage];

        return {
          labels: newLabels.slice(-20), // Keep the last 20 labels
          datasets: [
            {
              ...prevData.datasets[0],
              data: newPositionData.slice(-20), // Keep the last 20 data points for Position
            },
            {
              ...prevData.datasets[1],
              data: newVoltageData.slice(-20), // Keep the last 20 data points for Voltage
            },
          ],
        };
      });
    });

    return () => socket.close();
  }, []);

  return (
    <div>
      <div style={{ width: '600px', height: '400px' }}>
        <Line
          data={data}
          options={{
            animation: false,
            plugins: {
              legend: {
                display: true, // Displays the legend with options to toggle datasets
              },
            },
            scales: {
              x: {
                type: 'time',
                time: {
                  unit: 'second',
                  tooltipFormat: 'PPpp', // Display full timestamp in tooltip
                },
                title: {
                  display: true,
                  text: 'Timestamp',
                },
                ticks: {
                  autoSkip: true,
                  maxTicksLimit: 10,
                },
              },
              y: {
                title: {
                  display: true,
                  text: 'Value',
                },
              },
            },
          }}
        />
      </div>
    </div>
  );
};

export default Graph;
