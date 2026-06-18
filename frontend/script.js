async function sendMessage() {

    const input = document.getElementById("message");
    const chatBox = document.getElementById("chat-box");

    const message = input.value;

    if (!message) return;

    chatBox.innerHTML += `
        <div class="user">
            <b>You:</b> ${message}
        </div>
    `;

    input.value = "";

    const response = await fetch(
        "http://127.0.0.1:8000/chat",
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                message: message
            })
        }
    );

    const data = await response.json();

    chatBox.innerHTML += `
        <div class="ai">
            <b>AI:</b> ${data.answer}
        </div>
    `;

    chatBox.scrollTop = chatBox.scrollHeight;
}