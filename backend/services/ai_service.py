from openai import OpenAI
from dotenv import load_dotenv
import os
load_dotenv()
client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)
def get_ai_response(messages):
    response = client.chat.completions.create(
        model="openai/gpt-4o-mini",
        messages=messages
    )
    print("\nFULL RESPONSE:")
    print(response)
    return response.choices[0].message.content