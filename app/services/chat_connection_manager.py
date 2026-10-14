from collections import defaultdict
from fastapi import WebSocket


class ChatConnectionManager:
    def __init__(self):
        self.connections = defaultdict(
            lambda: defaultdict(set)
        )

    async def connect(
        self,
        request_id: int,
        user_id: int,
        websocket: WebSocket
    ) -> None:    
        await websocket.accept()
        self.connections[request_id][user_id].add(websocket)    

    def disconnect(
        self,
        request_id: int,
        user_id: int,
        websocket: WebSocket
    ) -> None: 
        user_connections = self.connections[request_id][user_id]
        user_connections.discard(websocket)

        if not user_connections:
            del self.connections[request_id][user_id]

        if not self.connections[request_id]:
            del self.connections[request_id]        

    async def broadcast(
        self,
        request_id: int,
        message: dict
    ) -> None:
        for user_connections in self.connections[request_id].values():
            for websocket in list(user_connections):
                await websocket.send_json(message)        

chat_manager = ChatConnectionManager()                