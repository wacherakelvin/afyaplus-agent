import os
import time
import asyncio
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()
async_client = AsyncOpenAI()

patient_messages = [
    "I have a persistent cough for two weeks",
    "My child has a rash on their arms",
    "I feel dizzy when I stand up quickly"
]

SYSTEM_PROMPT = "You are the AfyaPlus Health Assistant. Provide brief, safe guidance in 2-3 sentences."

async def process_patient(message, patient_id):
    response = await async_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": message}
        ],
        temperature=0.3,
        max_tokens=100
    )
    return f"Patient {patient_id}: {response.choices[0].message.content}"

async def main():
    start_time = time.time()
    tasks = [process_patient(msg, i) for i, msg in enumerate(patient_messages, 1)]
    results = await asyncio.gather(*tasks)
    for result in results:
        print(result)
        print()
    total_time = time.time() - start_time
    print(f"Total time (asynchronous): {total_time:.2f} seconds")

asyncio.run(main())