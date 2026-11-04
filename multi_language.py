import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()

SYSTEM_PROMPT = (
    "You are an AfyaPlus health assistant. "
    "Detect the language of the patient's message and respond in the SAME language. "
    "If they write in Swahili, respond in Swahili. "
    "If they write in English, respond in English. "
    "If they mix languages (Sheng), match their style. "
    "Provide brief, safe guidance and never diagnose."
)

test_messages = [
    "I have a fever and headache for two days",
    "Nina maumivu ya kichwa kwa siku tatu"
]

for msg in test_messages:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": msg}
        ],
        temperature=0.3,
        max_tokens=200
    )
    print(f"Patient: {msg}")
    print(f"Assistant: {response.choices[0].message.content}\n")