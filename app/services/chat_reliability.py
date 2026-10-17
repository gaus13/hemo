import asyncio 
from fastapi import WebSocket
from starlette.websockets import WebSocketDisconnect

HEARTBEAT_INTERVAL_SECONDS = 25
HEARTBEAT_TIMEOUT_SECONDS = 60

async def send_heartbeat(websocket: WebSocket) -> None:
    try:
        while True:
            await asyncio.sleep(
                HEARTBEAT_INTERVAL_SECONDS
            )

            await websocket.send_json(
                {
                    "type": "ping",
                }
            )

    except(
        asyncio.CancelledError,
        WebSocketDisconnect,
        RuntimeError
    ):
        return        

    # Heartbeat messages prove that the connection is still alive.