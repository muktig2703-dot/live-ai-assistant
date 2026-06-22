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
from fastapi.responses import PlainTextResponse
from services.ai_service import (get_ai_response, get_ai_vision_response,stream_ai_response)
from services.document_service import extract_text
from tools.search_tool import search_web
from agents.search_agent import needs_search
from fastapi.responses import FileResponse
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from services.image_service import encode_image
from fastapi.responses import StreamingResponse

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
    get_document,
    create_share_link,
    get_shared_chat
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
    model: str


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

    if file.filename.lower().endswith(
    (".pdf", ".docx", ".txt")
):

       document_text = extract_text(
        file_path
    )

       save_document(
        chat_id,
        file.filename,
        document_text,
        file_path
    )

    else:

      document_text = ""

      save_document(
        chat_id,
        file.filename,
        "",
        file_path
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
    selected_model = request.model
    print("REQUEST MODEL =", request.model)
    print("SELECTED MODEL =", selected_model)
    document = get_document(chat_id)

    document_name = ""
    document_content = ""
    document_path = ""
    is_image = False

    if document:

     document_name = document["filename"]

     document_content = document["content"]

     document_path = document["file_path"]

     is_image = False

    if document_path.lower().endswith(
    (".png", ".jpg", ".jpeg")
):
       is_image = True

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

LANGUAGE RULES:

- Always detect the language of the user's latest message.
- Reply in the same language.
- If the user writes in Hindi, reply in Hindi.
- If the user writes in English, reply in English.
- If the user writes in Tamil, reply in Tamil.
- If the user writes in Telugu, reply in Telugu.
- If the user mixes languages (Hinglish), reply naturally in the same mixed style.
- Do not translate unless the user explicitly asks.

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

    if is_image:

        base64_image = encode_image(
        document_path
    )

        answer = get_ai_vision_response(
        user_message,
        base64_image
    )

        save_message(
        chat_id,
        "assistant",
        answer
    )
  
        return {
        "answer": answer
    }

    else:

        return StreamingResponse(
            stream_ai_response(
            messages,
            selected_model,
            chat_id
        ),
        media_type="text/plain"
    )

    save_message(
        chat_id,
        "assistant",
        answer
    )

    return {
        "answer": answer
    }
#-----------------------------------------------
#EXPORT CHAT
#-----------------------------------------------
@app.get("/chat/{chat_id}/export")
def export_chat(chat_id: int):

    messages = get_messages(chat_id)

    content = ""

    for message in messages:

        content += (
            f"{message['role'].upper()}:\n"
            f"{message['content']}\n\n"
        )

    return PlainTextResponse(content)

@app.get("/chat/{chat_id}/export/pdf")
def export_chat_pdf(chat_id: int):

    messages = get_messages(chat_id)

    filename = f"chat_{chat_id}.pdf"

    doc = SimpleDocTemplate(filename)

    styles = getSampleStyleSheet()

    elements = []

    elements.append(
        Paragraph(
            "Live AI Assistant Chat Export",
            styles["Title"]
        )
    )

    elements.append(
        Spacer(1, 20)
    )

    for message in messages:

        role = message["role"].upper()

        content = message["content"]

        elements.append(
            Paragraph(
                f"<b>{role}</b>",
                styles["Heading3"]
            )
        )

        elements.append(
            Paragraph(
                content,
                styles["BodyText"]
            )
        )

        elements.append(
            Spacer(1, 10)
        )

    doc.build(elements)

    return FileResponse(
        filename,
        media_type="application/pdf",
        filename=filename
    )

@app.post("/chat/{chat_id}/share")
def share_chat(chat_id: int):

    token = create_share_link(chat_id)

    return {
        "share_url":
        f"http://127.0.0.1:5500/share.html?token={token}"
    }

@app.get("/shared/{token}")
def shared_chat(token: str):

    chat_id = get_shared_chat(token)

    if not chat_id:

        return {
            "error": "Chat not found"
        }

    return get_messages(chat_id)

@app.get("/search")
def search_chats(q: str):

    chats = get_chats()

    results = []

    for chat in chats:

        messages = get_messages(
            chat["id"]
        )

        found = False
        preview = ""

        for message in messages:

            if q.lower() in message["content"].lower():

                found = True

                preview = (
                    message["content"][:80]
                    + "..."
                )

                break

        if (
            found
            or q.lower() in chat["title"].lower()
        ):

            results.append({
                "chat_id": chat["id"],
                "title": chat["title"],
                "preview": preview
            })

    return results