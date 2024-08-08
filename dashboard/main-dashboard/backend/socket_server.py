import asyncio
import json
import lcm
import websockets
from exlcm import quad_state_t, enabled_t
import socket
import threading
from time import sleep

OPI_ADDR = ("10.42.0.199", 7668)

class DataHandler:
    def __init__(self):
        self.data = None
        self.enabled = False
        self.boolean_data = None
        self.lc = lcm.LCM("udpm://239.255.76.67:7667?ttl=1") # For sending data only
        self.opi_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.opi_socket.bind(OPI_ADDR)


    def get_data(self):
        return self.data


    def refresh_opi_data(self):
        while True:
            # print("Checking for opi data...")
            inc_data = data_handler.opi_socket.recv(4096)
            # Wait for data to be available
            while inc_data is None:
                inc_data = data_handler.opi_socket.recv(4096)
                sleep(0.05)
            
            message = quad_state_t.decode(inc_data)
            self.data = {
                "timestamp": message.timestamp, 
                "position": message.position, 
                "velocity": message.velocity, 
                "bus_voltage": message.bus_voltage,
                "fault_code": message.fault_code,
                "enabled": data_handler.enabled
            }
            # print(f"Data received from opi: {data_handler.data}")

    
    def handle_websocket_message(self, message):
        # Handle received WebSocket message (expected to be a boolean)
        self.boolean_data = json.loads(message)
        enable_command = enabled_t()
        enable_command.enabled = self.boolean_data['enabled']
        print(f"Received enable command: {enable_command.enabled}")
        self.lc.publish("ENABLED", enable_command.encode())
        self.enabled = self.boolean_data['enabled']
        print(f"Published boolean data: {self.boolean_data}")


data_handler = DataHandler()

async def send_opi_data_to_websocket(websocket):
    last_timestamp = 0
    while True:
        inc_data = data_handler.get_data()
        if inc_data is None or last_timestamp == inc_data["timestamp"]:
            asyncio.sleep(0.05)
            continue

        # Send data over WebSocket
        out_data = json.dumps(inc_data)
        await websocket.send(out_data)

        # print('Data sent to dashboard!')
        
        await asyncio.sleep(0.1)

async def receive_data(websocket):
    async for message in websocket:
        data_handler.handle_websocket_message(message)

async def websocket_server():
    async with websockets.serve(lambda ws, path: asyncio.gather(send_opi_data_to_websocket(ws), receive_data(ws)), "localhost", 8080):
        print("WebSocket server is running on ws://localhost:8080")
        await asyncio.Future()  # Run the server forever
        
def main():
    opi_thread = threading.Thread(target=data_handler.refresh_opi_data, daemon=True)
    opi_thread.start()

    asyncio.run(websocket_server())


if __name__ == "__main__":
    main()
