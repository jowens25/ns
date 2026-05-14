import asyncio
from websockets.asyncio.client import connect


async def hello():
    # Establish connection using a context manager
    async with connect("ws://127.0.0.1:8080/tech") as websocket:
        await websocket.send("JACOB")

        while True:
            message = await websocket.recv()
            print(f"Received: {message}")


if __name__ == "__main__":
    asyncio.run(hello())
