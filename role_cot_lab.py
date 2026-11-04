import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()

def run_triage_reasoning(symptom_report):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.2,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an expert emergency triage nurse at AfyaPlus Health. "
                    "Analyse the user symptoms. You MUST explain your clinical "
                    "reasoning step-by-step BEFORE concluding with a final directive. "
                    "Follow this EXACT structural layout:\n\n"
                    "REASONING STEPS:\n"
                    "- [Step 1]\n"
                    "- [Step 2]\n"
                    "FINAL DIRECTIVE: [Emergency Room / Clinic Appointment / Home Care]"
                )
            },
            {"role": "user", "content": symptom_report}
        ]
    )
    return response.choices[0].message.content

complex_case = (
    "I bumped my head an hour ago. I felt fine at first, "
    "but now I am getting dizzy and nauseous."
)
print(run_triage_reasoning(complex_case))