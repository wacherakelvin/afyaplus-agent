import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()

patient_message = "I have been feeling very tired for the past week and have no appetite."

print(f"Patient: {patient_message}")
print("Assistant: ", end="", flush=True)

try:
    stream = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are the AfyaPlus Health Assistant. Provide brief, empathetic guidance."},
            {"role": "user", "content": patient_message}
        ],
        temperature=0.3,
        max_tokens=200,
        stream=True
    )

    full_response = ""
    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            token = chunk.choices[0].delta.content
            print(token, end="", flush=True)
            full_response += token

    print()
    print("--- Streaming complete ---")
    print(f"Total response length: {len(full_response)} characters")
except Exception as e:
    print(f"\nError during streaming: {e}")