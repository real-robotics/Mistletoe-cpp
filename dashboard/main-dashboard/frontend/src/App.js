// src/App.js
import React from 'react';
import Graph from './components/Graph';
import './App.css';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>Real-time Data Graph</h1>
      </header>
      <Graph />
    </div>
  );
}

export default App;
