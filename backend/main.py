import os
import shutil
from fastapi import (
    FastAPI,
    UploadFile,
    File
)
from fastapi import Form
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from services.ai_service import get_ai_response
from services.document_service import extract_text
from tools.search_tool import search_web
from agents.search_agent import needs_search

from database.db import (
    init_db,
    create_chat,
    get_chats,
    rename_chat,
    delete_chat,
    toggle_pin,
    toggle_archive,
    save_message,
    get_messages,
    save_document,
    get_document
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()


# ----------------------------
# MODELS
# ----------------------------

class ChatRequest(BaseModel):
    chat_id: int
    message: str


class RenameRequest(BaseModel):
    title: str


# ----------------------------
# HOME
# ----------------------------

@app.get("/")
def home():
    return {
        "message": "Live AI Assistant Running"
    }


# ----------------------------
# CHAT MANAGEMENT
# ----------------------------

@app.post("/chat/new")
def new_chat():

    chat_id = create_chat()

    return {
        "chat_id": chat_id
    }


@app.get("/chats")
def chats():

    return get_chats()


@app.put("/chat/{chat_id}/rename")
def rename(chat_id: int, request: RenameRequest):

    rename_chat(chat_id, request.title)

    return {
        "message": "Chat renamed"
    }

@app.put("/chat/{chat_id}/pin")
def pin_chat(chat_id: int):

    toggle_pin(chat_id)

    return {
        "message": "Pin status updated"
    }

@app.put("/chat/{chat_id}/archive")
def archive_chat(chat_id: int):

    toggle_archive(chat_id)

    return {
        "message": "Archive status updated"
    }


@app.delete("/chat/{chat_id}")
def remove_chat(chat_id: int):

    delete_chat(chat_id)

    return {
        "message": "Chat deleted"
    }


@app.get("/chat/{chat_id}/history")
def history(chat_id: int):

    return get_messages(chat_id)


# ----------------------------
# FILE UPLOAD
# ----------------------------

@app.post("/upload")
async def upload_file(
    chat_id: int = Form(...),
    file: UploadFile = File(...)
):

    os.makedirs(
        "uploads",
        exist_ok=True
    )

    file_path = f"uploads/{file.filename}"

    with open(file_path, "wb") as buffer:

        shutil.copyfileobj(
            file.file,
            buffer
        )

    document_text = extract_text(
        file_path
    )

    save_document(
        chat_id,
        file.filename,
        document_text
    )

    return {
        "filename": file.filename,
        "characters": len(document_text)
    }

# ----------------------------
# AI CHAT
# ----------------------------

@app.post("/chat")
def chat(request: ChatRequest):

    chat_id = request.chat_id
    user_message = request.message
    document = get_document(chat_id)

    document_name = ""
    document_content = ""

    if document:

     document_name = document["filename"]

     document_content = document["content"]

    save_message(
        chat_id,
        "user",
        user_message
    )

    search_context = ""

    if needs_search(user_message):

        print("SEARCHING WEB...")

        search_results = search_web(user_message)

        for result in search_results:

            search_context += f"""
Title: {result['title']}
Content: {result['body']}

"""

    else:

        print("NO SEARCH NEEDED")

    messages = [
    {
        "role": "system",
        "content": f"""
You are a helpful AI assistant.

Use:

1. Conversation history
2. Search results
3. Uploaded document (if available)

Search Results:
{search_context}

Uploaded File:
{document_name}

Document Content:
{document_content[:12000]}
"""
        }
    ]

    messages.extend(
        get_messages(chat_id)
    )

    answer = get_ai_response(messages)

    save_message(
        chat_id,
        "assistant",
        answer
    )

    return {
        "answer": answer
    }