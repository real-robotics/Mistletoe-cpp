// server.js
const io = require('socket.io')(4000, {
    cors: {
      origin: "http://localhost:3000",
      methods: ["GET", "POST"]
    }
  });
  
  io.on('connection', (socket) => {
    console.log('Client connected');
    
    setInterval(() => {
      const data = {
        position: [Math.random(), Math.random(), Math.random(), Math.random()],
        velocity: [Math.random(), Math.random(), Math.random(), Math.random()],
        voltage: [Math.random() * 12, Math.random() * 12, Math.random() * 12, Math.random() * 12],
      };
      socket.emit('robot-data', data);
    }, 1000);
  
    socket.on('disconnect', () => {
      console.log('Client disconnected');
    });
  });