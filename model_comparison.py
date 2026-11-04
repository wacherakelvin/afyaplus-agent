import os
import time
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
cloud_client = OpenAI()
local_client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")

SYSTEM_PROMPT = "You are a health assistant. Provide brief, safe guidance."
patient_message = "I have chest pain when I breathe deeply"

messages = [
    {"role": "system", "content": SYSTEM_PROMPT},
    {"role": "user", "content": patient_message}
]

def timed_call(client, model_name):
    start = time.perf_counter()
    response = client.chat.completions.create(
        model=model_name,
        messages=messages,
        temperature=0.3,
        max_tokens=300
    )
    elapsed = time.perf_counter() - start
    return response.choices[0].message.content, elapsed

cloud_text, cloud_time = timed_call(cloud_client, "gpt-4o-mini")
local_text, local_time = timed_call(local_client, "llama3.2:1b")

print(f"{'Model':<20} {'Time (s)':<10} {'Length':<8} First 200 chars")
print("-" * 80)
print(f"{'gpt-4o-mini':<20} {cloud_time:<10.2f} {len(cloud_text):<8} {cloud_text[:200]!r}")
print(f"{'llama3.2':<20} {local_time:<10.2f} {len(local_text):<8} {local_text[:200]!r}")