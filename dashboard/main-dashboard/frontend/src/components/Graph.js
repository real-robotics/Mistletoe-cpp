// src/components/Graph.js
import React, { useEffect, useState } from 'react';
import { Line } from 'react-chartjs-2';
import { Box, FormControl, InputLabel, Select, MenuItem } from '@mui/material';
import {
  Chart,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  TimeScale,
} from 'chart.js';
import 'chartjs-adapter-date-fns';

Chart.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  TimeScale
);

const Graph = ({ socketData }) => {
  const [selectedPair, setSelectedPair] = useState(2);
  const [data, setData] = useState({
    labels: [],
    datasets: [
      {
        label: 'Position',
        data: [],
        borderColor: '#1e88e5', // Bright blue
        backgroundColor: 'rgba(30, 136, 229, 0.2)',
      },
      {
        label: 'Velocity',
        data: [],
        borderColor: '#ff6b6b', // Bright red
        backgroundColor: 'rgba(255, 107, 107, 0.2)',
      },
    ],
  });

  useEffect(() => {
    if (socketData) {
      const newData = socketData;
      setData((prevData) => {
        const newLabels = [...prevData.labels, newData.timestamp];
        const newPositionData = [
          ...prevData.datasets[0].data,
          newData.position[selectedPair],
        ];
        const newVelocityData = [
          ...prevData.datasets[1].data,
          newData.velocity[selectedPair],
        ];

        return {
          labels: newLabels.slice(-20),
          datasets: [
            {
              ...prevData.datasets[0],
              data: newPositionData.slice(-20),
            },
            {
              ...prevData.datasets[1],
              data: newVelocityData.slice(-20),
            },
          ],
        };
      });
    }
  }, [socketData, selectedPair]);

  const handleChange = (event) => {
    setSelectedPair(parseInt(event.target.value));
  };

  return (
    <Box p={2}>
      <FormControl fullWidth variant="outlined" margin="normal">
        <InputLabel id="joint-select-label">Choose a Joint to Monitor:</InputLabel>
        <Select
          labelId="joint-select-label"
          id="joint-select"
          value={selectedPair}
          onChange={handleChange}
          label="Choose a Joint to Monitor"
          sx={{ color: '#c9d1d9' }} // Ensure the text color fits the dark theme
        >
          {Array.from({ length: 12 }, (_, i) => (
            <MenuItem key={i} value={i}>
              Joint {i + 1}
            </MenuItem>
          ))}
        </Select>
      </FormControl>
      <Box mt={4}>
        <Line
          data={data}
          options={{
            animation: false,
            plugins: {
              legend: {
                display: true,
                labels: {
                  color: '#c9d1d9', // Legend text color
                },
              },
            },
            scales: {
              x: {
                type: 'time',
                time: {
                  unit: 'second',
                  tooltipFormat: 'PPpp',
                },
                title: {
                  display: true,
                  text: 'Timestamp',
                  color: '#c9d1d9', // Axis label color
                },
                ticks: {
                  color: '#c9d1d9', // Tick mark color
                  autoSkip: true,
                  maxTicksLimit: 10,
                },
              },
              y: {
                title: {
                  display: true,
                  text: 'Value',
                  color: '#c9d1d9', // Axis label color
                },
                ticks: {
                  color: '#c9d1d9', // Tick mark color
                },
              },
            },
          }}
        />
      </Box>
    </Box>
  );
};

export default Graph;
