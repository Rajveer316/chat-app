from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from typing import Dict, List

app = FastAPI()

# Mount the static directory to serve HTML, CSS, JS
app.mount("/static", StaticFiles(directory="static"), name="static")

# Store chat room connections and usernames
rooms: Dict[str, List[WebSocket]] = {}
usernames: Dict[WebSocket, str] = {}

@app.get("/{room_id}", response_class=HTMLResponse)
async def get_room(room_id: str):
    # Serve the chat UI for a specific room
    with open("static/index.html", "r") as f:
        html = f.read()
    return HTMLResponse(content=html)

@app.websocket("/ws/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str):
    await websocket.accept()

    # Create a new room if it doesn't exist
    if room_id not in rooms:
        rooms[room_id] = []

    rooms[room_id].append(websocket)

    try:
        # First message is username
        username = await websocket.receive_text()
        usernames[websocket] = username

        # Notify others that someone joined
        for client in rooms[room_id]:
            if client != websocket:
                await client.send_json({
                    "type": "notification",
                    "message": f"{username} entered the chatroom."
                })

        # Chat loop
        while True:
            message = await websocket.receive_text()
            for client in rooms[room_id]:
                await client.send_json({
                    "type": "chat",
                    "from": username,
                    "message": message
                })

    except WebSocketDisconnect:
        rooms[room_id].remove(websocket)
        left_username = usernames.get(websocket, "Someone")
        usernames.pop(websocket, None)

        # Notify others that user left
        for client in rooms[room_id]:
            await client.send_json({
                "type": "notification",
                "message": f"{left_username} left the chatroom."
            })
