import os
from dotenv import load_dotenv

# Load .env file into environment variables
load_dotenv()

# Retrieve the key
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    print("ERROR: OPENAI_API_KEY not found in .env file")
elif not api_key.startswith("sk-"):
    print("WARNING: Key does not look like an OpenAI key (should start with 'sk-')")
else:
    masked = api_key[:7] + "..." + api_key[-4:]
    print(f"Key loaded successfully: {masked}")
    print(f"Length: {len(api_key)} characters")