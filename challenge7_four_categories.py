import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()

def classify(new_patient_query):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.0,
        messages=[
            {"role": "system",
             "content": "Classify incoming user medical queries into exactly "
                        "one category: CRITICAL, NON_URGENT, ROUTINE, or EMERGENCY_DISPATCH."},
            {"role": "user",
             "content": "Query: I cannot breathe and my left arm feels numb."},
            {"role": "assistant", "content": "Category: CRITICAL"},
            {"role": "user",
             "content": "Query: I need to renew my allergy pills next month."},
            {"role": "assistant", "content": "Category: ROUTINE"},
            # NEW: EMERGENCY_DISPATCH example
            {"role": "user",
             "content": "Query: I fell down stairs and there is massive bleeding from my leg."},
            {"role": "assistant", "content": "Category: EMERGENCY_DISPATCH"},
            # Live target
            {"role": "user", "content": f"Query: {new_patient_query}"}
        ]
    )
    return response.choices[0].message.content

print(classify("I have a small bruise on my knee"))
# Expected: Category: NON_URGENT (or ROUTINE)

print(classify("Severe bleeding that will not stop after 20 minutes"))
# Expected: Category: EMERGENCY_DISPATCH