from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from typing import List, Dict

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

# Store connected users per room
rooms: Dict[str, List[WebSocket]] = {}
usernames: Dict[WebSocket, str] = {}

@app.get("/{room_id}", response_class=HTMLResponse)
async def get_room(room_id: str):
    with open("static/index.html") as f:
        return HTMLResponse(content=f.read())

@app.websocket("/ws/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str):
    await websocket.accept()
    
    # Add user to room
    if room_id not in rooms:
        rooms[room_id] = []
    rooms[room_id].append(websocket)

    try:
        # First message should be the username
        init_data = await websocket.receive_text()
        username = init_data.strip()
        usernames[websocket] = username

        # Notify others
        for client in rooms[room_id]:
            if client != websocket:
                await client.send_json({"type": "notification", "message": f"{username} entered the chatroom."})

        while True:
            data = await websocket.receive_text()
            for client in rooms[room_id]:
                await client.send_json({"type": "chat", "from": username, "message": data})

    except WebSocketDisconnect:
        rooms[room_id].remove(websocket)
        left_user = usernames.get(websocket, "Someone")
        for client in rooms[room_id]:
            await client.send_json({"type": "notification", "message": f"{left_user} left the chatroom."})
        usernames.pop(websocket, None)
