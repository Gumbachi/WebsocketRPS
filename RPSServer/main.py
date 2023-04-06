import asyncio

from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI()

class ConnectionManager:
    def __init__(self):
        self.connection_one: WebSocket = None
        self.connection_two: WebSocket = None

        self.p1move: str = None
        self.p2move: str = None


    @property
    def game_is_full(self) -> bool:
        return self.connection_one and self.connection_two
    
    @property
    def both_players_moved(self) -> bool:
        return self.p1move  and self.p2move

    async def connect(self, websocket: WebSocket):
        await websocket.accept()

        if self.connection_one is None:
            self.connection_one = websocket
            # print("Player One Connected!")
            return await websocket.send_text("You are Player One!")
        
        if self.connection_two is None:
            self.connection_two = websocket
            # print("Player Two Connected!")
            return await websocket.send_text("You are Player Two!")

        websocket.close(reason="Game is full go away")

    def process_message(self, websocket: WebSocket, message: str):
        if websocket == self.connection_one:
            if message in ("rock", "paper", "scissors"):
                # print(f"Player One played {message}")
                self.p1move = message
                return

        if websocket == self.connection_two:
            if message in ("rock", "paper", "scissors"):
                # print(f"Player Two played {message}")
                self.p2move = message
                return


        print(f"Ignoring unstructured data: {message}")

    
    async def reset(self):
        
        self.p1move = None
        self.p2move = None

        if self.connection_one:
            c = self.connection_one
            self.connection_one = None
            await c.close()
        if self.connection_two:
            c = self.connection_two
            self.connection_two = None
            await c.close()
        
        

    async def broadcast(self, message: str):
        if self.connection_one:
            await self.connection_one.send_text(message)

        if self.connection_two:
            await self.connection_two.send_text(message)


manager = ConnectionManager()

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    print("Waiting for connections...")
    await manager.connect(websocket)

    while not manager.game_is_full:
        await asyncio.sleep(1)
        
    
    await manager.broadcast("GO") # let clients know they can move

    # print("Players Connected... Ready to start")
    # print("Waiting for both players to send a move")

    try:
        while True:
            data = await websocket.receive_text()
            manager.process_message(websocket, message=data)
            if manager.both_players_moved:
                # print("Both Players have moved: game is completed and I dont know who won")
                break

        await manager.broadcast(f"GAME FINISHED\nP1: {manager.p1move}\nP2: {manager.p2move}")
        await manager.reset()
            
    except WebSocketDisconnect:
        await manager.broadcast("Someone left the game. Shutting Down")
        await manager.reset()