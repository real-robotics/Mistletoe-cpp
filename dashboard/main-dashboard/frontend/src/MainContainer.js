import React from 'react';
import Graph from './components/Graph';
import ToggleButton from './components/ToggleButton';
import BusVoltageDisplay from './components/BusVoltageDisplay';
import FaultMessage from './components/FaultMessage';
import './styles.css';

const MainContainer = ({ socket, socketData }) => {
  return (
    <>
      <header className="header">
        <h1>Mistletoe Operator Dashboard</h1>
      </header>
      <div className="container">

        <div className="content">
          <div className="left-panel">
            <ToggleButton socket={socket} socketData={socketData}/>
            <button className="button teleoperated-button">Teleoperated</button>
            <BusVoltageDisplay socketData={socketData} />
            <FaultMessage socketData={socketData} />
          </div>
          <div className="graph-container">
            <Graph socketData={socketData} />
          </div>
        </div>
      </div>
    </>

  );
};

export default MainContainer;
