from openai import OpenAI
from dotenv import load_dotenv
from fastapi.responses import StreamingResponse
import os
load_dotenv()
client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)
def get_ai_response(messages, model):

    try:

        response = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=1000
        )

        return response.choices[0].message.content

    except Exception as e:

        print(e)

        return f"Model Error: {str(e)}"
    
from database.db import save_message

def stream_ai_response(
    messages,
    model,
    chat_id
):

    print("STREAM MODEL =", model)

    full_response = ""

    stream = client.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=1000,
        stream=True
    )

    for chunk in stream:

        if (
            chunk.choices
            and chunk.choices[0].delta.content
        ):

            content = chunk.choices[0].delta.content

            full_response += content

            yield content

    save_message(
        chat_id,
        "assistant",
        full_response
    )

def get_ai_vision_response(
    prompt,
    base64_image
):

    response = client.chat.completions.create(

        model="openai/gpt-4o-mini",

        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url":
                            f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ]
    )

    return response.choices[0].message.content