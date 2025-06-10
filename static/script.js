let userName = "";
let ws = null;
let roomName = "";

function getName() {
  document.getElementById("namePrompt").style.display = "block";
}

function setName() {
  const name = document.getElementById("nameInput").value;
  if (name.trim()) {
    userName = name.trim();
    document.getElementById("namePrompt").style.display = "none";
    document.getElementById("chatUI").style.display = "block";
    connectWebSocket();
  }
}

function connectWebSocket() {
  const params = new URLSearchParams(window.location.search);
  roomName = params.get("room") || "default";
  ws = new WebSocket(`ws://${window.location.host}/ws/${roomName}`);

  ws.onopen = () => {
    ws.send(JSON.stringify({
      type: "join",
      user: userName
    }));
  };

  ws.onmessage = (event) => {
    const msgData = JSON.parse(event.data);

    if (msgData.type === "chat") {
      displayMessage(msgData);

      // Send read receipt
      ws.send(JSON.stringify({
        type: "read",
        id: msgData.id,
        user: userName
      }));
    }

    if (msgData.type === "read") {
      const statusEl = document.getElementById(`status-${msgData.id}`);
      if (statusEl) {
        statusEl.innerText = "✔✔️";
        statusEl.style.color = "blue";
      }
    }

    if (msgData.type === "system") {
      const msgBox = document.getElementById("chatBox");
      const line = document.createElement("div");
      line.style.color = "gray";
      line.textContent = msgData.message;
      msgBox.appendChild(line);
      msgBox.scrollTop = msgBox.scrollHeight;
    }

    if (msgData.type === "users") {
      const list = document.getElementById("userList");
      list.innerHTML = "<b>Active Users:</b><br>";
      msgData.users.forEach(user => {
        list.innerHTML += `<div>${user}</div>`;
      });
    }
  };
}

function sendMessage() {
  const input = document.getElementById("msgInput");
  const text = input.value.trim();
  if (text && ws) {
    const id = crypto.randomUUID();
    const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    const msg = {
      id,
      type: "chat",
      user: userName,
      message: text,
      timestamp: time
    };
    ws.send(JSON.stringify(msg));

    const msgBox = document.getElementById("chatBox");
    const line = document.createElement("div");
    line.innerHTML = `<b>[You]</b> ${text} <span style="font-size:12px;color:gray;">(${time}) <span id="status-${id}">✔️</span></span>`;
    msgBox.appendChild(line);
    msgBox.scrollTop = msgBox.scrollHeight;

    input.value = "";
  }
}

function displayMessage(msg) {
  const msgBox = document.getElementById("chatBox");
  const line = document.createElement("div");
  line.innerHTML = `<b>[${msg.user}]</b> ${msg.message} <span style="font-size:12px;color:gray;">(${msg.timestamp})</span>`;
  msgBox.appendChild(line);
let socket;
let username = "";
let urlParts = window.location.pathname.split('/');
let roomId = urlParts[urlParts.length - 1] || "default";

}

function joinChat() {
    username = document.getElementById("username").value.trim();
    if (!username) {
        alert("Please enter your name!");
        return;
    }

    // Hide login, show chat
    document.getElementById("login-section").style.display = "none";
    document.getElementById("chat-section").style.display = "block";

    // Connect WebSocket
   let protocol = window.location.protocol === "https:" ? "wss" : "ws";
socket = new WebSocket(`${protocol}://${window.location.host}/ws/${roomId}`);


    socket.onopen = () => {
        // Send the username first
        socket.send(JSON.stringify({ username: username }));
    };

    socket.onmessage = (event) => {
        const data = JSON.parse(event.data);

        if (data.type === "chat") {
            document.getElementById("chat-box").innerHTML += `<p><strong>${data.from}:</strong> ${data.message}</p>`;
            // Send read receipt
            socket.send(JSON.stringify({ type: "read" }));
        } else if (data.type === "notification") {
            document.getElementById("chat-box").innerHTML += `<p><em>${data.message}</em></p>`;
            updateUserList(data.users);
        } else if (data.type === "read") {
            document.getElementById("chat-box").innerHTML += `<p><em>${data.from} read the message</em></p>`;
        }
    };

    socket.onclose = () => {
        alert("Disconnected from server.");
    };
}

function sendMessage() {
    const input = document.getElementById("message-input");
    const message = input.value.trim();
    if (message && socket) {
        socket.send(JSON.stringify({ message: message }));
        input.value = "";
    }
}

function updateUserList(users) {
    const userList = document.getElementById("user-list");
    userList.innerHTML = "<strong>Active users:</strong><br>" + users.map(u => `• ${u}`).join("<br>");
}

