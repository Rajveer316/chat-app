let ws;
let username = "";
let roomId = window.location.pathname.split("/")[1];

document.getElementById("joinBtn").onclick = function () {
    const nameInput = document.getElementById("nameInput");
    username = nameInput.value.trim();

    if (!username) {
        alert("Please enter your name.");
        return;
    }

    document.getElementById("joinScreen").style.display = "none";
    document.getElementById("chatScreen").style.display = "block";

    connectWebSocket();
};

function connectWebSocket() {
    ws = new WebSocket(`wss://${window.location.host}/ws/${roomId}`);

    ws.onopen = () => {
        ws.send(username); // Send username as the first message
    };

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        const chatBox = document.getElementById("chatBox");

        if (data.type === "chat") {
            chatBox.innerHTML += `<div><strong>${data.from}:</strong> ${data.message}</div>`;
        } else if (data.type === "notification") {
            chatBox.innerHTML += `<div style="color: gray;"><em>${data.message}</em></div>`;
        }

        chatBox.scrollTop = chatBox.scrollHeight;
    };
}

document.getElementById("sendBtn").onclick = function () {
    const messageInput = document.getElementById("messageInput");
    const message = messageInput.value.trim();

    if (!message) return;

    ws.send(message);
    messageInput.value = "";
};
