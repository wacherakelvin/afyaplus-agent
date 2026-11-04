import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()

messages = [
    {
        "role": "system",
        "content": (
            "You are a helpful health assistant for AfyaPlus Health. "
            "Provide general health guidance. Never diagnose conditions "
            "or prescribe medication. Always recommend consulting a "
            "healthcare professional for serious concerns."
        )
    },
    {
        "role": "user",
        "content": "I have been having headaches for three days. Should I be worried?"
    }
]

try:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.3,
        max_tokens=300
    )

    ai_message = response.choices[0].message.content
    usage = response.usage

    print("--- AfyaPlus Health Assistant ---")
    print(f"Patient: I have been having headaches for three days. Should I be worried?")
    print(f"Assistant: {ai_message}")
    print(f"--- Usage Statistics ---")
    print(f"Prompt tokens: {usage.prompt_tokens}")
    print(f"Response tokens: {usage.completion_tokens}")
    print(f"Total tokens: {usage.total_tokens}")

except Exception as e:
    print(f"Error calling OpenAI API: {e}")
    print("Please check your API key and network connection.")