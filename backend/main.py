from fastapi import FastAPI
from pydantic import BaseModel

from services.ai_service import get_ai_response
from tools.search_tool import search_web
from agents.search_agent import needs_search

app = FastAPI()

# Conversation memory
chat_history = []


class ChatRequest(BaseModel):
    message: str


@app.get("/")
def home():
    return {
        "message": "Live AI Assistant Running"
    }


@app.post("/chat")
def chat(request: ChatRequest):

    user_message = request.message

    # Save user message
    chat_history.append({
        "role": "user",
        "content": user_message
    })

    search_context = ""

    # Agent decides whether search is needed
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

The search has already been performed for you.

DO NOT perform additional searches.
DO NOT request tool calls.

Use:
1. Conversation history
2. Search results (if available)

Search Results:
{search_context}
"""
        }
    ]

    # Add memory
    messages.extend(chat_history)

    # Get AI response
    answer = get_ai_response(messages)

    # Save assistant reply
    chat_history.append({
        "role": "assistant",
        "content": answer
    })

    return {
        "answer": answer
    }