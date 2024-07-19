import asyncio
import json
import random
import datetime
import websockets

async def send_data(websocket):
    while True:
        timestamp = datetime.datetime.utcnow().isoformat()
        position = random.random() * 100
        voltage = random.random() * 5

        data = json.dumps({"timestamp": timestamp, "position": position, "voltage": voltage})
        await websocket.send(data)
        
        await asyncio.sleep(0.1)  # Send data every 100 milliseconds

async def main():
    async with websockets.serve(send_data, "localhost", 8080, ping_interval=None):
        print("WebSocket server is running on ws://localhost:8080")
        await asyncio.Future()  # Run the server forever

asyncio.run(main())
