import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# Load from env with sensible defaults
base_url = os.getenv("MODEL_BASE_URL", "https://api.openai.com/v1")
model_name = os.getenv("MODEL_NAME", "gpt-4o-mini")
api_key = os.getenv("OPENAI_API_KEY", "ollama")

client = OpenAI(base_url=base_url, api_key=api_key)

response = client.chat.completions.create(
    model=model_name,
    messages=[{"role": "user", "content": "Say hello"}]
)
print(response.choices[0].message.content)
