// src/MainContainer.js
import React from 'react';
import { Container, Grid, Box, Typography } from '@mui/material';
import Graph from './components/Graph';
import ToggleButton from './components/ToggleButton';
import BusVoltageDisplay from './components/BusVoltageDisplay';
import FaultMessage from './components/FaultMessage';

const MainContainer = ({ socket, socketData }) => {
  return (
    <Box
      sx={{
        backgroundColor: '#0d1117', // Dark background for the main area
        minHeight: '100vh', // Ensures the full height is covered
        padding: 3,
      }}
    >
      <Container maxWidth="lg">
        <Typography
          variant="h4"
          component="h1"
          sx={{
            color: '#c9d1d9', // Light text color for the heading
            marginBottom: 4, // Spacing below the heading
            textAlign: 'left', // Left-align the heading
          }}
        >
          Mistletoe Operator Dashboard
        </Typography>
        <Grid container spacing={4}>
          <Grid item xs={12} md={3}>
            <Box
              sx={{
                border: '1px solid #30363d',
                backgroundColor: '#161b22',
                borderRadius: 2,
                padding: 2,
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'flex-start', // Align items to the start
                justifyContent: 'flex-start', // Start at the top
                gap: 2, // Ensure there's a small gap between components
              }}
            >
              <Box sx={{ width: '100%' }}>
                <ToggleButton socket={socket} socketData={socketData} />
              </Box>
              <Box sx={{ width: '100%' }}>
                <BusVoltageDisplay socketData={socketData} />
              </Box>
              <Box sx={{ width: '100%' }}>
                <FaultMessage socketData={socketData} />
              </Box>
            </Box>
          </Grid>
          <Grid item xs={12} md={9}>
            <Box
              sx={{
                border: '1px solid #30363d',
                backgroundColor: '#161b22',
                borderRadius: 2,
                padding: 2,
              }}
            >
              <Typography
                p={2}
                variant="h5"
                sx={{
                  color: '#c9d1d9', // Light text color
                  textAlign: 'left', // Left-align the text
                }}
                style={{fontWeight: 'bold'}}
              >
                Joint Position/Velocity Graph
              </Typography>
              <Graph socketData={socketData} />
            </Box>
          </Grid>
        </Grid>
      </Container>
    </Box>
  );
};

export default MainContainer;
