let currentChatId = null;
let voiceEnabled = true;
let currentChatTitle = "";
let controller = null;
let editingMessage = null;

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
    ${marked.parse(message.content)}
</div>

                        <div class="timestamp">
                            ${getCurrentTime()}
                        </div>

                    </div>

                </div>
            `;
        }
    });
document
    .querySelectorAll("pre")
    .forEach((pre) => {

        if (
            !pre.querySelector(".copy-btn")
        ) {

            const button =
                document.createElement("button");

            button.className =
                "copy-btn";

            button.innerText =
                "Copy";

            button.onclick = () =>
                copyCode(button);

            pre.prepend(button);
        }

    });

document
    .querySelectorAll("pre code")
    .forEach((block) => {

        hljs.highlightElement(block);

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

    const token =
    localStorage.getItem(
        "token"
    );

const response = await fetch(
    "http://127.0.0.1:8000/chat/new",
    {
        method: "POST",

        headers: {
            Authorization:
                `Bearer ${token}`
        }
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

    const welcome =
document.getElementById("welcome-screen");

if (welcome) {

    welcome.style.display = "none";
}

    if (!message) return;
    if (editingMessage) {

    const nextMessage =
        editingMessage.nextElementSibling;

    if (
        nextMessage &&
        nextMessage.classList.contains(
            "ai-message"
        )
    ) {
        nextMessage.remove();
    }

    editingMessage.remove();

    editingMessage = null;
}

    if (
    currentChatTitle === "New Chat" &&
    message.length > 0
) {

    const title =
        message.substring(0, 30);
    const token =
    localStorage.getItem("token");

await fetch(
    `http://127.0.0.1:8000/chat/${currentChatId}/rename`,
    {
        method: "PUT",

        headers: {
            "Content-Type": "application/json",
            Authorization:
                `Bearer ${token}`
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

            <div
                class="bubble user-bubble"
            >
                ${message}
            </div>

            <div class="timestamp">
                ${getCurrentTime()}
            </div>

            <div class="message-actions">

                <button
                    class="edit-btn"
                    onclick="editMessage(this)"
                >
                    ✏️
                </button>

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
   const selectedModel =
    document.getElementById(
        "model-select"
    ).value;
    document.getElementById(
    "stop-btn"
).style.display = "inline-block";
        controller = new AbortController();
        const token =
    localStorage.getItem("token");

const response = await fetch(
    "http://127.0.0.1:8000/chat",
    {
        method: "POST",
        headers: {
            "Content-Type":
                "application/json",

            Authorization:
                `Bearer ${token}`
        },
                signal: controller.signal,

                body: JSON.stringify({
    chat_id: currentChatId,
    message: message,
    model: selectedModel
})
            }
        );
    document.getElementById(loadingId)?.remove();

const aiMessageId =
    "ai-" + Date.now();

chatBox.innerHTML += `
    <div class="message ai-message">

        <div class="avatar ai-avatar">
            🤖
        </div>

        <div class="message-content">

            <div
                class="bubble"
                id="${aiMessageId}"
            ></div>

            <div class="timestamp">
                ${getCurrentTime()}
            </div>

<div class="message-actions">

    <button
        class="regen-btn"
        onclick="regenerateResponse(this)"
    >
        🔄 Regenerate
    </button>

</div>

        </div>

    </div>
`;

const aiBubble =
    document.getElementById(
        aiMessageId
    );

const reader =
    response.body.getReader();

const decoder =
    new TextDecoder();

let fullResponse = "";

while (true) {

    const {
        done,
        value
    } = await reader.read();

    if (done) break;

    const chunk =
    decoder.decode(
        value,
        { stream: true }
    );

    fullResponse += chunk;

    aiBubble.innerHTML =
        marked.parse(fullResponse);

    document
        .querySelectorAll("pre code")
        .forEach((block) => {

            hljs.highlightElement(
                block
            );

        });

    chatBox.scrollTop =
        chatBox.scrollHeight;
}

document.getElementById(
    "stop-btn"
).style.display = "none";

document
    .querySelectorAll("pre")
    .forEach((pre) => {

        if (
            !pre.querySelector(".code-header")
        ) {

            const code =
                pre.querySelector("code");

            let language =
                "Code";

            if (
                code &&
                code.className.includes(
                    "language-"
                )
            ) {

                language =
                    code.className
                        .replace(
                            "language-",
                            ""
                        )
                        .toUpperCase();
            }

            const header =
                document.createElement("div");

            header.className =
                "code-header";

            header.innerHTML = `
                <span>${language}</span>

                <button
                    class="copy-btn"
                    onclick="copyCode(this)"
                >
                    Copy
                </button>
            `;

            pre.prepend(header);
        }

    });
speak(fullResponse);


    }

    catch (error) {

    document.getElementById(
        "stop-btn"
    ).style.display = "none";

    if (error.name === "AbortError") {

        console.log(
            "Generation stopped by user"
        );

        return;
    }

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

async function regenerateResponse(button) {

    const userMessages =
        document.querySelectorAll(
            ".user-message .bubble"
        );

    if (
        userMessages.length === 0
    ) return;

    const lastUserMessage =
        userMessages[
            userMessages.length - 1
        ].innerText;

    document.getElementById(
        "message"
    ).value = lastUserMessage;

    sendMessage();
}

function editMessage(button) {

    editingMessage =
        button.closest(
            ".user-message"
        );

    const bubble =
        editingMessage.querySelector(
            ".user-bubble"
        );

    document.getElementById(
        "message"
    ).value =
        bubble.innerText;

    document.getElementById(
        "message"
    ).focus();
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

    const speech =
        new SpeechSynthesisUtterance(text);

    speech.rate = 1;
    speech.pitch = 1;
    speech.volume = 1;

    const voices =
        speechSynthesis.getVoices();

        const lower =
    text.toLowerCase();

    if (

    /[\u0900-\u097F]/.test(text)

    ||

    lower.includes("namaste")

    ||

    lower.includes("mera")

    ||

    lower.includes("aap")

    ||

    lower.includes("hai")

) {

        speech.lang = "hi-IN";

        const hindiVoice =
            voices.find(v =>
                v.lang.includes("hi")
            );

        if (hindiVoice) {
            speech.voice = hindiVoice;
        }
    }

    else {

        speech.lang = "en-US";
    }

    window.speechSynthesis.cancel();

    window.speechSynthesis.speak(speech);
}


const messageInput =
    document.getElementById(
        "message"
    );

if (messageInput) {

    messageInput.addEventListener(
        "keypress",
        function(event) {

            if (event.key === "Enter") {

                sendMessage();

            }
        }
    );
}

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

    const token =
    localStorage.getItem(
        "token"
    );

const response = await fetch(
    "http://127.0.0.1:8000/chats",
    {
        headers: {
            Authorization:
                `Bearer ${token}`
        }
    }
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

    const token =
        localStorage.getItem("token");

    await fetch(
        `http://127.0.0.1:8000/chat/${chatId}/rename`,
        {
            method: "PUT",

            headers: {
                "Content-Type": "application/json",
                Authorization:
                    `Bearer ${token}`
            },

            body: JSON.stringify({
                title: newTitle
            })
        }
    );

    loadChats();
}

async function deleteChat(chatId) {

    const token =
        localStorage.getItem(
            "token"
        );

    const confirmDelete = confirm(
        "Delete this chat?"
    );

    if (!confirmDelete) return;

    await fetch(
        `http://127.0.0.1:8000/chat/${chatId}`,
        {
            method: "DELETE",

            headers: {
                Authorization:
                    `Bearer ${token}`
            }
        }
    );

    document.getElementById(
        "chat-box"
    ).innerHTML = "";

    loadChats();
}

async function pinChat(chatId) {

    const token =
        localStorage.getItem(
            "token"
        );

    await fetch(
        `http://127.0.0.1:8000/chat/${chatId}/pin`,
        {
            method: "PUT",

            headers: {
                Authorization:
                    `Bearer ${token}`
            }
        }
    );

    loadChats();
}

async function archiveChat(chatId) {

    const token =
        localStorage.getItem(
            "token"
        );

    await fetch(
        `http://127.0.0.1:8000/chat/${chatId}/archive`,
        {
            method: "PUT",

            headers: {
                Authorization:
                    `Bearer ${token}`
            }
        }
    );

    loadChats();
}


async function openChat(chatId, chatTitle) {

    currentChatId = chatId;
    loadChats();
    currentChatTitle = chatTitle;

    const token =
    localStorage.getItem("token");

const response = await fetch(
    `http://127.0.0.1:8000/chat/${chatId}/history`,
    {
        headers: {
            Authorization:
                `Bearer ${token}`
        }
    }
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
    ${marked.parse(message.content)}
</div>

                    </div>

                </div>
            `;
        }
    });
document
    .querySelectorAll("pre")
    .forEach((pre) => {

        if (
            !pre.querySelector(".copy-btn")
        ) {

            const button =
                document.createElement("button");

            button.className =
                "copy-btn";

            button.innerText =
                "Copy";

            button.onclick = () =>
                copyCode(button);

            pre.prepend(button);
        }

    });

document
    .querySelectorAll("pre code")
    .forEach((block) => {

        hljs.highlightElement(block);

    });
    chatBox.scrollTop =
        chatBox.scrollHeight;
}

if (
    document.getElementById(
        "chat-list"
    )
) {

    loadChats();

}

function selectFile() {

    document
        .getElementById("file-input")
        .click();
}

const fileInput =
    document.getElementById(
        "file-input"
    );

if (fileInput) {

    fileInput.addEventListener(
        "change",
        uploadFile
    );
}

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

    const token =
        localStorage.getItem(
            "token"
        );

    const response =
        await fetch(
            "http://127.0.0.1:8000/upload",
            {
                method: "POST",

                headers: {
                    Authorization:
                        `Bearer ${token}`
                },

                body: formData
            }
        );

    const data =
        await response.json();

    alert(
        `Uploaded: ${data.filename}`
    );
}

async function filterChats() {

    const search =
        document
            .getElementById("chat-search")
            .value
            .trim();

    if (!search) {

        loadChats();
        return;
    }

    const response =
        await fetch(
            `http://127.0.0.1:8000/search?q=${encodeURIComponent(search)}`
        );

    const results =
        await response.json();

    const chatList =
        document.getElementById("chat-list");

    chatList.innerHTML = `
        <h3>🔍 Search Results</h3>
    `;

    results.forEach(result => {

        chatList.innerHTML += `
            <div
                class="chat-item"
                onclick="openChat(
                    ${result.chat_id},
                    '${result.title.replace(/'/g, "\\'")}'
                )"
            >

                <div>

                    <strong>
                        ${result.title}
                    </strong>

                    <br>

                    <small>
                        ${result.preview}
                    </small>

                </div>

            </div>
        `;
    });
}

async function exportChat() {

    if (!currentChatId) {

        alert(
            "Select a chat first."
        );

        return;
    }

    const token =
    localStorage.getItem("token");

const response =
    await fetch(
        `http://127.0.0.1:8000/chat/${currentChatId}/export`,
        {
            headers: {
                Authorization:
                    `Bearer ${token}`
            }
        }
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

    const token =
        localStorage.getItem(
            "token"
        );

    const response =
        await fetch(
            `http://127.0.0.1:8000/chat/${currentChatId}/export/pdf`,
            {
                headers: {
                    Authorization:
                        `Bearer ${token}`
                }
            }
        );

    const blob =
        await response.blob();

    const url =
        URL.createObjectURL(blob);

    const link =
        document.createElement("a");

    link.href = url;

    link.download =
        `${currentChatTitle}.pdf`;

    link.click();
}

async function shareChat() {

    if (!currentChatId) {

        alert(
            "Select a chat first."
        );

        return;
    }

    const token =
    localStorage.getItem("token");

const response =
    await fetch(
        `http://127.0.0.1:8000/chat/${currentChatId}/share`,
        {
            method: "POST",

            headers: {
                Authorization:
                    `Bearer ${token}`
            }
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

const dropZone =
    document.getElementById(
        "drop-zone"
    );

if (dropZone) {

    document.addEventListener(
        "dragover",
        (event) => {

            event.preventDefault();

            dropZone.classList.add(
                "active"
            );
        }
    );

document.addEventListener(
    "dragleave",
    () => {

        dropZone.classList.remove(
            "active"
        );
    }
);

document.addEventListener(
    "drop",
    async (event) => {

        event.preventDefault();

        dropZone.classList.remove(
            "active"
        );

        const file =
            event.dataTransfer.files[0];

        if (!file) return;

        if (!currentChatId) {

            alert(
                "Please select a chat first."
            );

            return;
        }

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

        const progressContainer =
    document.getElementById(
        "upload-progress-container"
    );

const progressBar =
    document.getElementById(
        "upload-progress-bar"
    );

progressContainer.style.display =
    "block";

const xhr = new XMLHttpRequest();

xhr.open(
    "POST",
    "http://127.0.0.1:8000/upload"
);

xhr.upload.onprogress =
    (event) => {

        if (event.lengthComputable) {

            const percent =
                (event.loaded / event.total) * 100;

            progressBar.style.width =
                percent + "%";
        }
    };

xhr.onload = () => {

    progressBar.style.width =
        "100%";

    setTimeout(() => {

        progressContainer.style.display =
            "none";

        progressBar.style.width =
            "0%";

    }, 1000);

    const data =
        JSON.parse(xhr.responseText);

    alert(
        `Uploaded: ${data.filename}`
    );
};
const token =
    localStorage.getItem("token");
console.log(token);
xhr.setRequestHeader(
    "Authorization",
    `Bearer ${token}`
);
xhr.send(formData);
 }
);}

function copyCode(button) {

    const pre =
        button.closest("pre");

    const code =
        pre.querySelector("code")
           .innerText;

    navigator.clipboard.writeText(code);

    button.innerText = "Copied!";

    setTimeout(() => {

        button.innerText = "Copy";

    }, 2000);
}

function copyResponse(button) {

    const text =
        button.dataset.content;

    navigator.clipboard
        .writeText(text);

    button.innerText =
        "✅ Copied";

    setTimeout(() => {

        button.innerText =
            "📋 Copy";

    }, 2000);
}

function stopGeneration() {

    if (controller) {

        controller.abort();

    }
}

speechSynthesis.onvoiceschanged =
    () => {

        speechSynthesis.getVoices();

    };

const token =
    localStorage.getItem("token");

const currentPage =
    window.location.pathname;

if (

    !token &&

    !currentPage.includes("login.html") &&
    !currentPage.includes("register.html") &&
    !currentPage.includes("home.html")

) {

    window.location.href =
        "login.html";
}

async function register() {

    const name =
        document.getElementById("name").value;

    const email =
        document.getElementById("email").value;

    const password =
        document.getElementById("password").value;

    const response = await fetch(
        "http://127.0.0.1:8000/register",
        {
            method: "POST",

            headers: {
                "Content-Type":
                    "application/json"
            },

            body: JSON.stringify({

                name: name,

                email: email,

                password: password

            })
        }
    );

    const data =
        await response.json();

    alert(
        data.message || data.error
    );

    if (data.message) {

        window.location.href =
            "login.html";
    }
}

async function login() {

    const email =
        document.getElementById("email").value;

    const password =
        document.getElementById("password").value;

    const response = await fetch(
        "http://127.0.0.1:8000/login",
        {
            method: "POST",

            headers: {
                "Content-Type":
                    "application/json"
            },

            body: JSON.stringify({

                email: email,

                password: password

            })
        }
    );

    const data =
        await response.json();

    if (data.access_token) {

    localStorage.setItem(
        "token",
        data.access_token
    );

    window.location.href =
        "chat.html";
}

else {

    alert(data.error);
} }

function logout() {

    localStorage.removeItem(
        "token"
    );

    window.location.href =
        "login.html";
}
function usePrompt(text) {

    document.getElementById("message").value = text;

    document.getElementById("message").focus();
}