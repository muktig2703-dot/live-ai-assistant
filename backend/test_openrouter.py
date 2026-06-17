from openai import OpenAI
from dotenv import load_dotenv
import os

print("Starting...")

load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")

print("Key found:", bool(api_key))

client = OpenAI(
    api_key=api_key,
    base_url="https://openrouter.ai/api/v1"
)

response = client.chat.completions.create(
    model="openai/gpt-oss-20b",
    messages=[
        {
            "role": "user",
            "content": "What is Python?"
        }
    ]
)

print("\nResponse:")
print(response.choices[0].message.content)