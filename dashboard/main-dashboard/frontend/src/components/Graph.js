// src/Graph.js
import React, { useEffect, useState } from 'react';
import { Line } from 'react-chartjs-2';
import { Chart, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, TimeScale } from 'chart.js';
import 'chartjs-adapter-date-fns';

Chart.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, TimeScale);

const Graph = ({ socketData }) => {
  const [selectedPair, setSelectedPair] = useState(2);
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
        label: 'Velocity',
        data: [],
        borderColor: 'rgba(192, 75, 75, 1)',
        backgroundColor: 'rgba(192, 75, 75, 0.2)',
      },
    ],
  });

  

  useEffect(() => {
    if (socketData) {
      const newData = socketData;
      setData((prevData) => {
        const newLabels = [...prevData.labels, newData.timestamp];
        const newPositionData = [...prevData.datasets[0].data, newData.position[selectedPair]];
        const newVelocityData = [...prevData.datasets[1].data, newData.velocity[selectedPair]];
        
        return {
          labels: newLabels.slice(-20), // Keep the last 20 labels
          datasets: [
            {
              ...prevData.datasets[0],
              data: newPositionData.slice(-20), // Keep the last 20 data points for Position
            },
            {
              ...prevData.datasets[1],
              data: newVelocityData.slice(-20), // Keep the last 20 data points for Velocity
            },
          ],
        };
      });
    }
  }, [socketData, selectedPair]);

  useEffect(() => {
    setData({
      labels: [],
      datasets: [
        {
          label: 'Position',
          data: [],
          borderColor: 'rgba(75, 192, 192, 1)',
          backgroundColor: 'rgba(75, 192, 192, 0.2)',
        },
        {
          label: 'Velocity',
          data: [],
          borderColor: 'rgba(192, 75, 75, 1)',
          backgroundColor: 'rgba(192, 75, 75, 0.2)',
        },
      ],
    })
  }, [selectedPair])


  const handleChange = (event) => {
    setSelectedPair(parseInt(event.target.value));
  };
  
  return (
    <div>
      <div>
        <label htmlFor="pair-select">Choose a pair:</label>
        <select id="pair-select" onChange={handleChange} value={selectedPair}>
          {Array.from({ length: 12 }, (_, i) => (
            <option key={i} value={i}>
              Pair {i + 1}
            </option>
          ))}
        </select>
      </div>
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
