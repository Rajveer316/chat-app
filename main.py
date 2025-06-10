from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from typing import Dict, List
import json

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

rooms: Dict[str, List[Dict]] = {}  # Each room has list of {"ws": WebSocket, "user": name}


@app.get("/")
def read_root():
    return HTMLResponse("<h2>Go to /static/index.html</h2>")


@app.websocket("/ws/{room}")
async def websocket_endpoint(websocket: WebSocket, room: str):
    await websocket.accept()
    username = None

    if room not in rooms:
        rooms[room] = []

    try:
        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)

            if msg.get("type") == "join":
                username = msg["user"]
                rooms[room].append({"ws": websocket, "user": username})

                # Notify all users someone joined
                await broadcast(room, {
                    "type": "system",
                    "message": f"{username} entered the chatroom."
                })

                # Send updated user list
                await broadcast_users(room)
                continue

            if msg.get("type") == "read":
                await broadcast_except(room, websocket, msg)
                continue

            if msg.get("type") == "chat":
                msg["status"] = "delivered"
                await broadcast_except(room, websocket, msg)

    except WebSocketDisconnect:
        if username:
            rooms[room] = [c for c in rooms[room] if c["ws"] != websocket]

            # Notify others someone left
            await broadcast(room, {
                "type": "system",
                "message": f"{username} left the chatroom."
            })

            await broadcast_users(room)


async def broadcast(room, message):
    for conn in rooms.get(room, []):
        await conn["ws"].send_text(json.dumps(message))


async def broadcast_except(room, sender_ws, message):
    for conn in rooms.get(room, []):
        if conn["ws"] != sender_ws:
            await conn["ws"].send_text(json.dumps(message))


async def broadcast_users(room):
    users = [c["user"] for c in rooms.get(room, [])]
    msg = {
        "type": "users",
        "users": users
    }
    await broadcast(room, msg)
