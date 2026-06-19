let voiceEnabled = true;

function getCurrentTime() {

    const now = new Date();

    return now.toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit"
    });
}


async function loadHistory() {

    const chatBox = document.getElementById("chat-box");

    const response = await fetch(
        "http://127.0.0.1:8000/history"
    );

    const messages = await response.json();

    chatBox.innerHTML = "";

    messages.forEach(message => {

        if (message.role === "user") {

            chatBox.innerHTML += `
                <div class="message user-message">

                    <div class="message-content">

                        <div class="bubble">
                            ${message.content}
                        </div>

                        <div class="timestamp">
                            ${getCurrentTime()}
                        </div>

                    </div>

                    <div class="avatar user-avatar">
                        👤
                    </div>

                </div>
            `;
        }

        else {

            chatBox.innerHTML += `
                <div class="message ai-message">

                    <div class="avatar ai-avatar">
                        🤖
                    </div>

                    <div class="message-content">

                        <div class="bubble">
                            ${message.content}
                        </div>

                        <div class="timestamp">
                            ${getCurrentTime()}
                        </div>

                    </div>

                </div>
            `;
        }
    });

    chatBox.scrollTop = chatBox.scrollHeight;
}


async function clearChat() {

    await fetch(
        "http://127.0.0.1:8000/history",
        {
            method: "DELETE"
        }
    );

    document.getElementById("chat-box").innerHTML = "";
}


async function sendMessage() {

    const input = document.getElementById("message");
    const chatBox = document.getElementById("chat-box");

    const message = input.value.trim();

    if (!message) return;

    chatBox.innerHTML += `
        <div class="message user-message">

            <div class="message-content">

                <div class="bubble">
                    ${message}
                </div>

                <div class="timestamp">
                    ${getCurrentTime()}
                </div>

            </div>

            <div class="avatar user-avatar">
                👤
            </div>

        </div>
    `;

    input.value = "";

    const loadingId = Date.now();

    chatBox.innerHTML += `
        <div class="message ai-message" id="${loadingId}">

            <div class="avatar ai-avatar">
                🤖
            </div>

            <div class="message-content">

                <div class="bubble loading">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>

            </div>

        </div>
    `;

    chatBox.scrollTop = chatBox.scrollHeight;

    try {

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

        document.getElementById(loadingId)?.remove();

        chatBox.innerHTML += `
            <div class="message ai-message">

                <div class="avatar ai-avatar">
                    🤖
                </div>

                <div class="message-content">

                    <div class="bubble">
                        ${data.answer}
                    </div>

                    <div class="timestamp">
                        ${getCurrentTime()}
                    </div>

                </div>

            </div>
        `;

        chatBox.scrollTop = chatBox.scrollHeight;

        speak(data.answer);

    }

    catch (error) {

        console.error(error);

        document.getElementById(loadingId)?.remove();

        chatBox.innerHTML += `
            <div class="message ai-message">

                <div class="avatar ai-avatar">
                    🤖
                </div>

                <div class="message-content">

                    <div class="bubble">
                        Error connecting to AI server.
                    </div>

                </div>

            </div>
        `;
    }
}


function toggleTheme() {

    document.body.classList.toggle("dark-mode");

    const btn = document.getElementById("theme-btn");

    if (document.body.classList.contains("dark-mode")) {
        btn.innerText = "☀️ Light Mode";
    }
    else {
        btn.innerText = "🌙 Dark Mode";
    }
}


function startListening() {

    const recognition =
        new webkitSpeechRecognition();

    recognition.lang = "en-US";

    recognition.start();

    recognition.onresult = function(event) {

        const transcript =
            event.results[0][0].transcript;

        document.getElementById(
            "message"
        ).value = transcript;
    };
}


function speak(text) {

    if (!voiceEnabled) return;

    if (!text) return;

    const speech = new SpeechSynthesisUtterance(text);

    speech.rate = 1;
    speech.pitch = 1;
    speech.volume = 1;

    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(speech);
}


document
    .getElementById("message")
    .addEventListener("keypress", function(event) {

        if (event.key === "Enter") {
            sendMessage();
        }
    });


loadHistory();

function toggleVoice() {

    voiceEnabled = !voiceEnabled;

    const btn = document.getElementById("voice-btn");

    if (voiceEnabled) {
        btn.innerText = "🔊 Voice ON";
    }
    else {
        btn.innerText = "🔇 Voice OFF";
        window.speechSynthesis.cancel();
    }
}