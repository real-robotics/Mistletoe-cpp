// server.js
const WebSocket = require('ws');

const wss = new WebSocket.Server({ port: 8080 });

wss.on('connection', (ws) => {
  console.log('Client connected');

  const sendData = () => {
    const timestamp = new Date().toISOString();
    const position = Math.random() * 100;
    const voltage = Math.random() * 5;

    const data = JSON.stringify({ timestamp, position, voltage });

    ws.send(data);
  };

  const intervalId = setInterval(sendData, 100);

  ws.on('close', () => {
    console.log('Client disconnected');
    clearInterval(intervalId);
  });
});

console.log('WebSocket server is running on ws://localhost:8080');
