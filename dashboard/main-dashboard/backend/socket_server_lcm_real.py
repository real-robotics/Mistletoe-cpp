import asyncio
import json
import threading
import lcm
import websockets
from concurrent.futures import ThreadPoolExecutor
from exlcm import data_t  # Import your LCM message type

# LCM message handler
class DataHandler:
    def __init__(self):
        self.data = None

    def handle_message(self, channel, data):
        # Decode LCM message
        message = data_t.decode(data)
        # Convert message to dictionary
        self.data = {
            "timestamp": message.timestamp,  # Assuming 'timestamp' field in data_t
            "position": message.position,    # Assuming 'position' field in data_t
            "voltage": message.voltage       # Assuming 'voltage' field in data_t
        }

    def get_data(self):
        return self.data

data_handler = DataHandler()

# Function to run LCM in a separate thread
def run_lcm():
    lc = lcm.LCM()
    lc.subscribe("EXAMPLE", data_handler.handle_message)
    while True:
        lc.handle()


async def send_data(websocket):
    while True:
        # Wait for data to be available
        while data_handler.get_data() is None:
            await asyncio.sleep(0.1)
        
        # Send data over WebSocket
        data = json.dumps(data_handler.get_data())
        await websocket.send(data)
        
        await asyncio.sleep(0.1)  # Send data every 100 milliseconds

async def websocket_server():
    async with websockets.serve(send_data, "localhost", 8080):
        print("WebSocket server is running on ws://localhost:8080")
        await asyncio.Future()  # Run the server forever
        
def start_websocket_server():
    # Start the asyncio event loop for WebSocket server
    asyncio.run(websocket_server())

def main():
    # Start LCM in a separate thread
    websocket_thread = threading.Thread(target=start_websocket_server, daemon=True)
    websocket_thread.start()

    lcm_thread = threading.Thread(target=run_lcm, daemon=True)
    lcm_thread.start()

    websocket_thread.join()
    lcm_thread.join()

if __name__ == "__main__":
    main()
