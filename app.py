import os
import json
import time
from dotenv import load_dotenv
from openai import OpenAI, APITimeoutError, APIError, RateLimitError

load_dotenv()

# --- PHASE 1: Architecture Setup ---
cloud_client = OpenAI()
local_client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")

PATIENT_MESSAGE = "I am 8 months pregnant and I have a severe headache and my vision is blurry. I feel dizzy."

# --- PHASE 3 & 4: Advanced Prompt & JSON Schema ---
SYSTEM_PROMPT = """
You are an expert automated triage engine for AfyaPlus Health. 
You MUST analyze the patient message using Chain-of-Thought reasoning.

CRITICAL INSTRUCTIONS:
1. Never include conversational fluff (no "Sure", "Here is the data").
2. You MUST output ONLY a raw JSON object matching this exact schema.
3. If the patient is pregnant AND has a severe headache OR vision changes, this is PREECLAMPSIA. You MUST set is_critical_emergency to true and route to "Emergency Room".

JSON Schema:
{
  "is_critical_emergency": boolean,
  "detected_symptoms": ["string", "string"],
  "clinical_reasoning_summary": "string",
  "routing_destination": "string"
}
"""

messages = [
    {"role": "system", "content": SYSTEM_PROMPT},
    {"role": "user", "content": f"Patient Message: {PATIENT_MESSAGE}"}
]

# --- PHASE 2: Programmatic Inference & Resilience ---
def get_triage_response():
    print("Attempting Cloud Inference (GPT-4o-mini)...")
    start_time = time.time()
    
    try:
        # Cloud Call with strict 4.0s timeout and JSON Mode
        response = cloud_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.0,
            timeout=4.0,  # Max 4.0 seconds per brief
            response_format={"type": "json_object"}
        )
        elapsed = time.time() - start_time
        print(f"Cloud Success in {elapsed:.2f} seconds.")
        return response.choices[0].message.content, "Cloud"
        
    except (APITimeoutError, APIError, RateLimitError) as e:
        print(f"Cloud Failed/Timed Out: {type(e).__name__}")
        print("INITIATING FALLBACK: Routing to Local Ollama (llama3.2:1b)...")
        
        # Local Fallback Call
        start_local = time.time()
        try:
            local_response = local_client.chat.completions.create(
                model="llama3.2:1b",
                messages=messages,
                temperature=0.0,
                response_format={"type": "json_object"}
            )
            elapsed_local = time.time() - start_local
            print(f"Local Success in {elapsed_local:.2f} seconds.")
            return local_response.choices[0].message.content, "Local"
            
        except Exception as local_err:
            print(f"Fatal Error: Both cloud and local failed. {local_err}")
            return None, "Failed"

# --- PHASE 5: End-to-End Demonstration ---
if __name__ == "__main__":
    raw_output, source = get_triage_response()
    
    if raw_output:
        try:
            # Parse the JSON
            parsed_data = json.loads(raw_output)
            
            print("\n" + "="*40)
            print(f"AFYAPLUS TRIAGE RESULT (Source: {source})")
            print("="*40)
            print(json.dumps(parsed_data, indent=4))
            
            print("\n--- ROUTING DECISION ---")
            
            # Validation Layer: If the model routed to Emergency Room, 
            # force the boolean to true regardless of what it output.
            is_emergency = parsed_data.get("is_critical_emergency", False)
            destination = parsed_data.get("routing_destination", "")
            
            if is_emergency or "emergency" in destination.lower():
                print(f"ESCALATE: Route to {destination} IMMEDIATELY.")
            else:
                print(f"STANDARD: Route to {destination}.")
                
        except json.JSONDecodeError:
            print("Error: The model failed to return valid JSON.")
            print("Raw output was:", raw_output)