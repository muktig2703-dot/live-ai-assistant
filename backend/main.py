import os
import shutil
from jose import jwt
from jose import JWTError
from datetime import datetime, timedelta
from fastapi import Header
from fastapi import HTTPException
from fastapi import Depends
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
from passlib.context import CryptContext
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
    get_shared_chat,
    create_user,
    get_user_by_email,
    chat_belongs_to_user
)

SECRET_KEY = "my_super_secret_key"

ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 60

def create_access_token(data):

    to_encode = data.copy()

    expire = (
        datetime.utcnow()
        + timedelta(
            minutes=
            ACCESS_TOKEN_EXPIRE_MINUTES
        )
    )

    to_encode.update(
        {"exp": expire}
    )

    encoded_jwt = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return encoded_jwt

def get_current_user(
    authorization: str = Header(None)
):
    print("AUTH HEADER =", authorization)
    if not authorization:

        raise HTTPException(
            status_code=401,
            detail="Not authenticated"
        )

    token = authorization.replace(
        "Bearer ",
        ""
    )

    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        user_id = payload.get(
            "user_id"
        )

        return user_id

    except JWTError:

        raise HTTPException(
            status_code=401,
            detail="Invalid token"
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

class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

class RenameRequest(BaseModel):
    title: str

class NewChatRequest(BaseModel):
    user_id: int


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
def new_chat(

    current_user = Depends(
        get_current_user
    )

):

    chat_id = create_chat(
        current_user
    )

    return {
        "chat_id": chat_id
    }


@app.get("/chats")
def chats(

    current_user = Depends(
        get_current_user
    )

):

    return get_chats(
        current_user
    )


@app.put("/chat/{chat_id}/rename")
def rename(
    chat_id: int,
    request: RenameRequest,
    current_user = Depends(
        get_current_user
    )
):

    if not chat_belongs_to_user(
        chat_id,
        current_user
    ):
        raise HTTPException(
            status_code=403,
            detail="Access denied"
        )

    rename_chat(
        chat_id,
        current_user,
        request.title
    )

    return {
        "message": "Chat renamed"
    }

@app.put("/chat/{chat_id}/pin")
def pin_chat(
    chat_id: int,
    current_user = Depends(
        get_current_user
    )
):

    if not chat_belongs_to_user(
        chat_id,
        current_user
    ):
        raise HTTPException(
            status_code=403,
            detail="Access denied"
        )

    toggle_pin(chat_id,current_user)

    return {
        "message": "Pin status updated"
    }

@app.put("/chat/{chat_id}/archive")
def archive_chat(
    chat_id: int,
    current_user = Depends(
        get_current_user
    )
):

    if not chat_belongs_to_user(
        chat_id,
        current_user
    ):
        raise HTTPException(
            status_code=403,
            detail="Access denied"
        )

    toggle_archive(chat_id,current_user)

    return {
        "message": "Archive status updated"
    }


@app.delete("/chat/{chat_id}")
def remove_chat(
    chat_id: int,
    current_user = Depends(
        get_current_user
    )
):

    if not chat_belongs_to_user(
        chat_id,
        current_user
    ):
        raise HTTPException(
            status_code=403,
            detail="Access denied"
        )

    delete_chat(chat_id,current_user)

    return {
        "message": "Chat deleted"
    }


@app.get("/chat/{chat_id}/history")
def history(
    chat_id: int,
    user_id: int = Depends(get_current_user)
):

    if not chat_belongs_to_user(
        chat_id,
        user_id
    ):

        raise HTTPException(
            status_code=403,
            detail="Access denied"
        )

    return get_messages(chat_id)


# ----------------------------
# FILE UPLOAD
# ----------------------------
@app.post("/upload")
async def upload_file(
    chat_id: int = Form(...),
    file: UploadFile = File(...),
    user_id: int = Depends(
        get_current_user
    )
):
    if not chat_belongs_to_user(
        chat_id,
        user_id
    ):
        raise HTTPException(
            status_code=403,
            detail="Access denied"
        )
    
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
def chat(
    request: ChatRequest,
    user_id: int = Depends(get_current_user)
):
    if not chat_belongs_to_user(
        request.chat_id,
        user_id
    ):
        raise HTTPException(
            status_code=403,
            detail="Access denied"
        )
    

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

IMPORTANT:

Always respond in the same language
used by the user.

Examples:

User: Hello, how are you?
Assistant: English

User: नमस्ते, आप कैसे हैं?
Assistant: Hindi in devnagari script

User: mera naam Mukti hai
Assistant: Hinglish using Roman letters

User: vanakkam
Assistant: Tamil

Never reply with language names
such as:

English
Hindi
Tamil
Telugu

Instead, answer the user's actual question
in that language.

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
def export_chat(
    chat_id: int,
    user_id: int = Depends(
        get_current_user
    )
):

    if not chat_belongs_to_user(
        chat_id,
        user_id
    ):
        raise HTTPException(
            status_code=403,
            detail="Access denied"
        )

    messages = get_messages(chat_id)

    content = ""

    for message in messages:

        content += (
            f"{message['role'].upper()}:\n"
            f"{message['content']}\n\n"
        )

    return PlainTextResponse(content)

@app.get("/chat/{chat_id}/export/pdf")
def export_chat_pdf(
    chat_id: int,
    user_id: int = Depends(
        get_current_user
    )
):

    if not chat_belongs_to_user(
        chat_id,
        user_id
    ):
        raise HTTPException(
            status_code=403,
            detail="Access denied"
        )

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
def share_chat(
    chat_id: int,
    user_id: int = Depends(
        get_current_user
    )
):

    if not chat_belongs_to_user(
        chat_id,
        user_id
    ):
        raise HTTPException(
            status_code=403,
            detail="Access denied"
        )

    token = create_share_link(
        chat_id
    )

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
def search_chats(
    q: str,
    current_user = Depends(
        get_current_user
    )
):

    chats = get_chats(
        current_user
    )

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

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

def hash_password(password):

    return pwd_context.hash(password)

def verify_password(
    plain_password,
    hashed_password
):

    return pwd_context.verify(
        plain_password,
        hashed_password
    )

@app.post("/register")
def register(
    request: RegisterRequest
):

    existing_user = get_user_by_email(
        request.email
    )

    if existing_user:

        return {
            "error":
            "Email already exists"
        }

    password_hash = hash_password(
        request.password
    )

    create_user(
        request.name,
        request.email,
        password_hash
    )

    return {
        "message":
        "User registered successfully"
    }

@app.post("/login")
def login(
    request: LoginRequest
):

    user = get_user_by_email(
        request.email
    )

    if not user:

        return {
            "error":
            "Invalid email or password"
        }

    valid_password = verify_password(
        request.password,
        user["password_hash"]
    )

    if not valid_password:

        return {
            "error":
            "Invalid email or password"
        }

    token = create_access_token(
    {
        "user_id": user["id"]
    }
)

    return {
    "access_token": token
}