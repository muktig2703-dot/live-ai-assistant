let currentChatId = null;
let voiceEnabled = true;
let currentChatTitle = "";

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

async function createNewChat() {

    const response = await fetch(
        "http://127.0.0.1:8000/chat/new",
        {
            method: "POST"
        }
    );

    const data = await response.json();

    currentChatId = data.chat_id;
    currentChatTitle = "New Chat";

    document.getElementById(
        "chat-box"
    ).innerHTML = "";

    loadChats();
}


async function sendMessage() {

    const input = document.getElementById("message");
    const chatBox = document.getElementById("chat-box");

    const message = input.value.trim();

    if (!message) return;

    if (
    currentChatTitle === "New Chat" &&
    message.length > 0
) {

    const title =
        message.substring(0, 30);

    await fetch(
        `http://127.0.0.1:8000/chat/${currentChatId}/rename`,
        {
            method: "PUT",
            headers: {
                "Content-Type":
                    "application/json"
            },
            body: JSON.stringify({
                title: title
            })
        }
    );

    currentChatTitle = title;

    await loadChats();
}

    if (!currentChatId) {

    alert("Please create or select a chat first.");

    return;
}

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
    chat_id: currentChatId,
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

async function loadChats() {

    const response = await fetch(
        "http://127.0.0.1:8000/chats"
    );

    const chats = await response.json();

    const chatList =
        document.getElementById("chat-list");

    chatList.innerHTML = "";

    // Pinned Section

    chatList.innerHTML += `
        <h3>📌 Pinned</h3>
    `;

    chats
        .filter(chat => chat.is_pinned && !chat.is_archived)
        .forEach(chat => {

            renderChat(chat);
        });

    // Regular Section

    chatList.innerHTML += `
        <h3>💬 Chats</h3>
    `;

    chats
        .filter(chat => !chat.is_pinned && !chat.is_archived)
        .forEach(chat => {

            renderChat(chat);
        });

    // Archived Section

    chatList.innerHTML += `
        <h3>📁 Archived</h3>
    `;

    chats
        .filter(chat => chat.is_archived)
        .forEach(chat => {

            renderChat(chat);
        });
}

function renderChat(chat) {

    const chatList =
        document.getElementById("chat-list");

    chatList.innerHTML += `
        <div
    class="chat-item ${
        chat.id === currentChatId
            ? "active-chat"
            : ""
    }"
    data-title="${chat.title.toLowerCase()}"
>

            <span
                onclick="openChat(${chat.id}, '${chat.title.replace(/'/g, "\\'")}')"
            >
                ${chat.title}
            </span>

            <div class="chat-actions">

                <button
                    onclick="pinChat(${chat.id})"
                >
                    📌
                </button>

                <button
                    onclick="archiveChat(${chat.id})"
                >
                    📁
                </button>

                <button
                    onclick="renameChat(${chat.id})"
                >
                    ✏️
                </button>

                <button
                    onclick="deleteChat(${chat.id})"
                >
                    🗑️
                </button>

            </div>

        </div>
    `;
}

async function renameChat(chatId) {

    const newTitle = prompt(
        "Enter new chat name:"
    );

    if (!newTitle) return;

    await fetch(
        `http://127.0.0.1:8000/chat/${chatId}/rename`,
        {
            method: "PUT",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                title: newTitle
            })
        }
    );

    loadChats();
}

async function deleteChat(chatId) {

    const confirmDelete = confirm(
        "Delete this chat?"
    );

    if (!confirmDelete) return;

    await fetch(
        `http://127.0.0.1:8000/chat/${chatId}`,
        {
            method: "DELETE"
        }
    );

    document.getElementById(
        "chat-box"
    ).innerHTML = "";

    loadChats();
}

async function pinChat(chatId) {

    await fetch(
        `http://127.0.0.1:8000/chat/${chatId}/pin`,
        {
            method: "PUT"
        }
    );

    loadChats();
}

async function archiveChat(chatId) {

    await fetch(
        `http://127.0.0.1:8000/chat/${chatId}/archive`,
        {
            method: "PUT"
        }
    );

    loadChats();
}


async function openChat(chatId, chatTitle) {

    currentChatId = chatId;
    loadChats();
    currentChatTitle = chatTitle;

    const response = await fetch(
        `http://127.0.0.1:8000/chat/${chatId}/history`
    );

    const messages = await response.json();

    const chatBox =
        document.getElementById("chat-box");

    chatBox.innerHTML = "";

    messages.forEach(message => {

        if (message.role === "user") {

            chatBox.innerHTML += `
                <div class="message user-message">
                    <div class="message-content">
                        <div class="bubble">
                            ${message.content}
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

                    </div>

                </div>
            `;
        }
    });

    chatBox.scrollTop =
        chatBox.scrollHeight;
}

loadChats();

function selectFile() {

    document
        .getElementById("file-input")
        .click();
}

document
    .getElementById("file-input")
    .addEventListener(
        "change",
        uploadFile
    );

    async function uploadFile(event) {

        if (!currentChatId) {

    alert(
        "Please select a chat first."
    );

    return;
}

    const file =
        event.target.files[0];

    if (!file) return;

    const formData =
        new FormData();

    formData.append(
        "file",
        file
    );

    formData.append(
    "chat_id",
    currentChatId
);

    const response =
        await fetch(
            "http://127.0.0.1:8000/upload",
            {
                method: "POST",
                body: formData
            }
        );

    const data =
        await response.json();

    alert(
        `Uploaded: ${data.filename}`
    );
}

function filterChats() {

    const search =
        document
            .getElementById("chat-search")
            .value
            .toLowerCase();

    const chats =
        document.querySelectorAll(".chat-item");

    chats.forEach(chat => {

        const title =
            chat.dataset.title;

        if (title.includes(search)) {

            chat.style.display = "flex";
        }

        else {

            chat.style.display = "none";
        }
    });
}

async function exportChat() {

    if (!currentChatId) {

        alert(
            "Select a chat first."
        );

        return;
    }

    const response =
        await fetch(
            `http://127.0.0.1:8000/chat/${currentChatId}/export`
        );

    const text =
        await response.text();

    const blob =
        new Blob(
            [text],
            { type: "text/plain" }
        );

    const link =
        document.createElement("a");

    link.href =
        URL.createObjectURL(blob);

    link.download =
    `${currentChatTitle}.txt`;

    link.click();
}

async function exportPDF() {

    if (!currentChatId) {

        alert(
            "Select a chat first."
        );

        return;
    }

    window.open(
        `http://127.0.0.1:8000/chat/${currentChatId}/export/pdf`,
        "_blank"
    );
}

async function shareChat() {

    if (!currentChatId) {

        alert(
            "Select a chat first."
        );

        return;
    }

    const response =
        await fetch(
            `http://127.0.0.1:8000/chat/${currentChatId}/share`,
            {
                method: "POST"
            }
        );

    const data =
        await response.json();

    navigator.clipboard.writeText(
        data.share_url
    );

    alert(
        "Share link copied!"
    );
}