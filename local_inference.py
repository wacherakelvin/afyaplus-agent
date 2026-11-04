from openai import OpenAI

# Connect to local Ollama instance (no API key needed)
client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"   # Ollama ignores this, but SDK requires something
)

messages = [
    {
        "role": "system",
        "content": (
            "You are a helpful health assistant for AfyaPlus Health. "
            "Provide general health guidance. Never diagnose conditions "
            "or prescribe medication."
        )
    },
    {
        "role": "user",
        "content": "I have been having headaches for three days. Should I be worried?"
    }
]

response = client.chat.completions.create(
   model="llama3.2:1b",
    messages=messages,
    temperature=0.3
)

print("--- Local Model Response ---")
print(response.choices[0].message.content)