from collections import defaultdict
from fastapi import WebSocket
from starlette.websockets import WebSocketDisconnect

# chat_connection_manager is an in-memory registry of connected WebSockets.
from collections import defaultdict

from fastapi import WebSocket
from starlette.websockets import WebSocketDisconnect


class ChatConnectionManager:
    def __init__(self):
        self.connections = defaultdict(
            lambda: defaultdict(set)
        )

    async def connect(
        self,
        request_id: int,
        user_id: int,
        websocket: WebSocket,
    ) -> None:
        await websocket.accept()
        self.connections[request_id][user_id].add(websocket)

    def disconnect(
        self,
        request_id: int,
        user_id: int,
        websocket: WebSocket,
    ) -> None:
        request_connections = self.connections.get(request_id)

        if request_connections is None:
            return

        user_connections = request_connections.get(user_id)

        if user_connections is None:
            return

        user_connections.discard(websocket)

        if not user_connections:
            del request_connections[user_id]

        if not request_connections:
            del self.connections[request_id]

    async def broadcast(
        self,
        request_id: int,
        message: dict,
    ) -> None:
        request_connections = self.connections.get(request_id)

        if request_connections is None:
            return

        dead_connections = []

        for user_id, user_connections in request_connections.items():
            for websocket in list(user_connections):
                try:
                    await websocket.send_json(message)
                except (
                    WebSocketDisconnect,
                    RuntimeError,
                ):
                    dead_connections.append(
                        (user_id, websocket)
                    )

        for user_id, websocket in dead_connections:
            self.disconnect(
                request_id=request_id,
                user_id=user_id,
                websocket=websocket,
            )

    async def close_all(self) -> None:
        for request_id, request_connections in list(
            self.connections.items()
        ):
            for user_id, user_connections in list(
                request_connections.items()
            ):
                for websocket in list(user_connections):
                    try:
                        await websocket.close(
                            code=1001,
                            reason="Server shutting down.",
                        )
                    except RuntimeError:
                        pass

                    self.disconnect(
                        request_id=request_id,
                        user_id=user_id,
                        websocket=websocket,
                    )


chat_manager = ChatConnectionManager()


"""we needed to change this file bcs Dead sockets can cause errors,
Missing requests can create empty entries, No shutdown cleanup, No connection limits, "The new reliable versions fix this"""