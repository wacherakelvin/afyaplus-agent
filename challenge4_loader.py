import os
import sys
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# TODO 1: Exit if key is None
if api_key is None:
    print("ERROR: OPENAI_API_KEY missing. Add it to .env")
    sys.exit(1)

# TODO 2: Exit if placeholder still present
if api_key == "sk-your-key-here":
    print("ERROR: You haven't replaced the placeholder key with a real one.")
    sys.exit(1)

# TODO 3: Print masked confirmation
masked = api_key[:7] + "..." + api_key[-4:]
print(f"Key loaded successfully: {masked}")