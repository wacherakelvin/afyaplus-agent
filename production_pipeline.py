import os
import time
from dotenv import load_dotenv
from openai import OpenAI, APITimeoutError, RateLimitError, APIError

load_dotenv()
client = OpenAI()

BLOCKED_PATTERNS = [
    "you have",
    "you should take",
    "diagnosis",
    "prescribe",
    "mg",
]

FALLBACK_RESPONSE = (
    "I am currently unable to process your request. "
    "For immediate assistance, please contact our helpline at +254-XXX-XXXX "
    "or visit your nearest healthcare facility."
)

def validate_response(response_text):
    lowered = response_text.lower()
    for pattern in BLOCKED_PATTERNS:
        if pattern in lowered:
            return False, f"Blocked: contains '{pattern}'"
    return True, "Passed"

def get_ai_response(patient_message, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are AfyaPlus Health Assistant. Provide safe, general health guidance. Never diagnose or prescribe."},
                    {"role": "user", "content": patient_message}
                ],
                temperature=0.3,
                max_tokens=200,
                timeout=10.0
            )
            ai_text = response.choices[0].message.content
            is_safe, reason = validate_response(ai_text)
            if not is_safe:
                print(f"  [SAFETY] Response blocked: {reason}")
                return FALLBACK_RESPONSE
            return ai_text
        except APITimeoutError:
            wait_time = 2 ** attempt
            print(f"  [RETRY] Timeout on attempt {attempt + 1}. Waiting {wait_time}s...")
            time.sleep(wait_time)
        except RateLimitError:
            wait_time = 5 * (attempt + 1)
            print(f"  [RETRY] Rate limited. Waiting {wait_time}s...")
            time.sleep(wait_time)
        except APIError as e:
            print(f"  [ERROR] API error: {e}")
            if attempt == max_retries - 1:
                break
    print("  [FALLBACK] All retries failed. Using fallback response.")
    return FALLBACK_RESPONSE

print("--- Production Pipeline Test ---")
test_messages = [
    "I have a mild headache today",
    "My chest hurts and I cannot breathe properly",
]
for msg in test_messages:
    print(f"Patient: {msg}")
    response = get_ai_response(msg)
    print(f"Assistant: {response}\n")