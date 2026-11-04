import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()

raw_patient_sms = (
    "Amani here. My 4-year-old child has had a hot body (fever) since yesterday "
    "and keeps vomiting. We are in a village near Kilifi. Please help us quickly, "
    "the child is very weak."
)

extraction_prompt = """
You are a backend administrative data extraction engine for AfyaPlus Health.
Analyse the following untrusted user SMS text. Extract the required parameters
into a valid JSON object matching this schema:
{
  "patient_age_years": integer or null,
  "symptoms": ["string", "string"],
  "location_cluster": "string",
  "requires_emergency_dispatch": boolean
}
CRITICAL: Do not include any markdown formatting (no triple-backtick json fences)
or any conversational text. Return ONLY the raw JSON string.
"""

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": extraction_prompt},
        {"role": "user", "content": f"SMS: {raw_patient_sms}"}
    ],
    temperature=0.0,
    response_format={"type": "json_object"}
)

parsed = json.loads(response.choices[0].message.content)
print("--- Automated API Extraction Complete ---")
print(json.dumps(parsed, indent=2))

if parsed.get("requires_emergency_dispatch"):
    print(f"ALERT: Dispatching emergency SMS to {parsed['location_cluster']} "
          f"medical team for a patient aged {parsed['patient_age_years']}.")
else:
    print("System Status: Staging ticket in standard queue.")
    extraction_prompt = """
You are a backend administrative data extraction engine for AfyaPlus Health.
Return a valid JSON object matching this schema:
{
  "patient_age_years": integer or null,
  "symptoms": ["string", "string"],
  "location_cluster": "string",
  "requires_emergency_dispatch": boolean,
  "severity_score": integer 1-10
}
Severity scoring rule:
- 1-3 = mild (minor cough, sore throat, mild headache)
- 4-7 = moderate (persistent symptoms, mild fever)
- 8-10 = severe (high fever in young child, vomiting, weakness, breathing issues)
CRITICAL: Return ONLY raw JSON, no markdown.
"""

# After parsing:
if parsed.get("severity_score", 0) >= 8:
    print(f"HIGH SEVERITY (score={parsed['severity_score']}) - notifying on-call physician")