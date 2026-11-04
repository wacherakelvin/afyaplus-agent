import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()

patient_case = (
    "Hello AfyaPlus, I am Chidinma. I am 7 months pregnant with my third child. "
    "For the past two days, I have had a severe headache that will not go away and "
    "my feet are suddenly very swollen. I feel safe waiting for my appointment next week."
)

# V1: Naive
prompt_v1 = f"""
Look at this message from a patient and tell me if it is dangerous: "{patient_case}"
"""

# V2: Role + template
prompt_v2 = f"""
You are an expert obstetric triage nurse at AfyaPlus Health. Analyse the patient
message for life-threatening third-trimester complications, specifically signs of
high blood pressure, preeclampsia (severe headaches, vision changes, sudden
swelling), or bleeding.

Provide your output exactly like this:
RISK LEVEL: [CRITICAL / NORMAL]
ACTION REQUIRED: [IMMEDIATE OUTREACH / STANDARD FOLLOWUP]
SUMMARY: [1-sentence explanation]

Patient Message: "{patient_case}"
"""

# V3: Defensive CoT + guardrails
prompt_v3 = f"""
You are a defensive, automated triage routing system for AfyaPlus Health. Your
role is to categorise patient intake text to flag high-risk pregnancy complications.

CRITICAL INSTRUCTIONS:
1. Analyse the text step-by-step for high-risk flags: preeclampsia markers
   (persistent headache + peripheral edema), premature labour, or fluid loss.
2. Do NOT offer a medical diagnosis. Do NOT prescribe medications.
3. Keep tone completely objective. No conversational openings.

Use this exact output format:
THOUGHT PROCESS:
- [Step-by-step clinical evaluation of symptoms]
FINAL STATUS: [CRITICAL_URGENT / ROUTINE_CARE]
ROUTING DESTINATION: [Emergency Medical Call Team / General Queue]

Patient Message: "{patient_case}"
"""

prompts = [prompt_v1, prompt_v2, prompt_v3]
for index, current_prompt in enumerate(prompts, 1):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": current_prompt}],
        temperature=0.0
    )
    print(f"====== PROMPT VERSION {index} OUTPUT ======")
    print(response.choices[0].message.content)
    print()