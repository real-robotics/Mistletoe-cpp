import asyncio
import websockets

async def listen():
    uri = "ws://localhost:8080"
    async with websockets.connect(uri) as websocket:
        while True:
            data = await websocket.recv()
            print(f"Received data: {data}")

asyncio.run(listen())
