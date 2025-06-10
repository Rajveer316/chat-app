let socket;
let username = "";
let roomId = window.location.pathname.split('/').pop(); // Extract room name from URL

function joinChat() {
    username = document.getElementById("username").value.trim();
    if (!username) {
        alert("Please enter your name!");
        return;
    }

    document.getElementById("login-section").style.display = "none";
    document.getElementById("chat-section").style.display = "block";

    const protocol = window.location.protocol === "https:" ? "wss" : "ws";
    socket = new WebSocket(`${protocol}://${window.location.host}/ws/${roomId}`);

    socket.onopen = () => {
        socket.send(username); // Send username first
    };

    socket.onmessage = (event) => {
        const data = JSON.parse(event.data);

        if (data.type === "chat") {
            document.getElementById("chat-box").innerHTML += `<p><strong>${data.from}:</strong> ${data.message}</p>`;
        } else if (data.type === "notification") {
            document.getElementById("chat-box").innerHTML += `<p><em>${data.message}</em></p>`;
        }

        document.getElementById("chat-box").scrollTop = document.getElementById("chat-box").scrollHeight;
    };

    socket.onerror = (error) => {
        console.error("WebSocket error:", error);
    };
}

function sendMessage() {
    const input = document.getElementById("message-input");
    const message = input.value.trim();
    if (message && socket) {
        socket.send(message);
        input.value = "";
    }
}
