// src/utils/websocket.js
export const connectWebSocket = (url, onMessageCallback) => {
  const socket = new WebSocket(url);
  socket.onmessage = (event) => {
    onMessageCallback(JSON.parse(event.data));
  };
  return socket;
};

export const sendWebSocketMessage = (socket, message) => {
  if (socket && socket.readyState === WebSocket.OPEN) {
    socket.send(JSON.stringify(message));
  }
};
