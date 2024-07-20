import asyncio
import json
import random
import datetime
import websockets

connected_clients = set()

async def send_data():
    while True:
        timestamp = datetime.datetime.utcnow().isoformat()
        position = [random.random() * 5 for _ in range(12)]
        velocity = [random.random() * 5 for _ in range(12)]

        data = json.dumps({"timestamp": timestamp, "position": position, "velocity": velocity})

        if connected_clients:
            await asyncio.wait([client.send(data) for client in connected_clients])
        
        await asyncio.sleep(0.1)  # Send data every 100 milliseconds

async def handle_client(websocket, path):
    connected_clients.add(websocket)
    try:
        async for message in websocket:
            data = json.loads(message)
            if data.get('type') == 'toggleButton':
                print(f"Button enabled: {data['enabled']}")
    finally:
        connected_clients.remove(websocket)

async def main():
    server = await websockets.serve(handle_client, "localhost", 8080, ping_interval=None)
    print("WebSocket server is running on ws://localhost:8080")
    
    await asyncio.gather(
        server.wait_closed(),
        send_data()
    )

asyncio.run(main())
