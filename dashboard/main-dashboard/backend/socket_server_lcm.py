import asyncio
import json
import threading
import lcm
import websockets
from concurrent.futures import ThreadPoolExecutor
from exlcm import quad_state_t, enabled_t # Import your LCM message type

# TODO: refractor bad GPT code to make more sense

# LCM message handler
class DataHandler:
    def __init__(self):
        self.data = None
        self.enabled = False
        self.boolean_data = None  # For receiving boolean data
        self.lc = lcm.LCM(
            "udpm://239.255.76.67:7667?ttl=1"
            )

    def handle_message(self, channel, data):
        # Decode LCM message
        message = quad_state_t.decode(data)
        # Convert message to dictionary
        self.data = {
            "timestamp": message.timestamp,  # Assuming 'timestamp' field in data_t
            "position": message.position,    # Assuming 'position' field in data_t
            "velocity": message.velocity,       # Assuming 'velocity' field in data_t
            "bus_voltage": message.bus_voltage,
            "fault_code": message.fault_code,
            "enabled": self.enabled
        }
        # print('recieved lcm message')
        print(message.position)

    def get_data(self):
        return self.data

    def handle_websocket_message(self, message):
        # Handle received WebSocket message (expected to be a boolean)
        self.boolean_data = json.loads(message)
        enable_command = enabled_t()
        enable_command.enabled = self.boolean_data['enabled']
        self.lc.publish("ENABLED", enable_command.encode())
        self.enabled = self.boolean_data['enabled']
        print(f"Published boolean data: {self.boolean_data}")

data_handler = DataHandler()

# Function to run LCM in a separate thread
def run_lcm():
    lc = lcm.LCM(
        # "udpm://239.255.76.67:7667?ttl=1"
        )
    lc.subscribe("STATE_C2C", data_handler.handle_message)
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

        # print('data sent')
        
        await asyncio.sleep(0.1)  # Send data every 100 milliseconds

async def receive_data(websocket):
    async for message in websocket:
        data_handler.handle_websocket_message(message)

async def websocket_server():
    async with websockets.serve(lambda ws, path: asyncio.gather(send_data(ws), receive_data(ws)), "localhost", 8080):
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
