from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# Serve static files like index.html, JS, CSS from /static
app.mount("/static", StaticFiles(directory="static"), name="static")

# Active connections per room
rooms = {}

# Active users (username by connection)
usernames = {}

# Serve index.html at root "/"
@app.get("/", response_class=HTMLResponse)
async def get_index():
    with open("static/index.html") as f:
        return HTMLResponse(f.read())

@app.websocket("/ws/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str):
    await websocket.accept()

    if room_id not in rooms:
        rooms[room_id] = []

    # Receive name from user
    name_data = await websocket.receive_json()
    username = name_data.get("username", "Anonymous")
    usernames[websocket] = username
    rooms[room_id].append(websocket)

    # Notify all others in the room
    await broadcast(room_id, {
        "type": "notification",
        "message": f"{username} entered the chatroom.",
        "users": [usernames.get(ws, "") for ws in rooms[room_id]]
    })

    try:
        while True:
            data = await websocket.receive_json()
            message = data.get("message", "")
            if message:
                await broadcast(room_id, {
                    "type": "chat",
                    "from": username,
                    "message": message
                })

            # Handle read receipts
            if data.get("type") == "read":
                await broadcast(room_id, {
                    "type": "read",
                    "from": username
                })

    except WebSocketDisconnect:
        rooms[room_id].remove(websocket)
        await broadcast(room_id, {
            "type": "notification",
            "message": f"{username} left the chatroom.",
            "users": [usernames.get(ws, "") for ws in rooms[room_id]]
        })
        del usernames[websocket]

async def broadcast(room_id, data: dict):
    to_remove = []
    for ws in rooms[room_id]:
        try:
            await ws.send_json(data)
        except:
            to_remove.append(ws)
    for ws in to_remove:
        rooms[room_id].remove(ws)
        usernames.pop(ws, None)
