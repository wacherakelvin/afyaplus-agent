import os
import time
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()

patient_messages = [
    "I have a persistent cough for two weeks",
    "My child has a rash on their arms",
    "I feel dizzy when I stand up quickly"
]

SYSTEM_PROMPT = "You are the AfyaPlus Health Assistant. Provide brief, safe guidance in 2-3 sentences."

start_time = time.time()
for i, message in enumerate(patient_messages, 1):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": message}
        ],
        temperature=0.3,
        max_tokens=100
    )
    print(f"Patient {i}: {message}")
    print(f"Response: {response.choices[0].message.content}\n")

total_time = time.time() - start_time
print(f"Total time (synchronous): {total_time:.2f} seconds")
print(f"Average per patient: {total_time/3:.2f} seconds")