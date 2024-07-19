// src/websocket.js
export function connectWebSocket(url, onMessage) {
    const socket = new WebSocket(url);
  
    socket.onopen = () => {
      console.log('WebSocket connection opened');
    };
  
    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      onMessage(data);
    };
  
    socket.onclose = () => {
      console.log('WebSocket connection closed');
    };
  
    socket.onerror = (error) => {
      console.error('WebSocket error', error);
    };
  
    return socket;
  }
  