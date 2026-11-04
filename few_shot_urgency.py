import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()

def analyse_patient_urgency_few_shot(new_patient_query):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.0,
        messages=[
            {"role": "system",
             "content": "Classify incoming user medical queries into exactly "
                        "one category: CRITICAL, NON_URGENT, or ROUTINE."},
            # Few-shot example 1: CRITICAL
            {"role": "user",
             "content": "Query: I cannot breathe and my left arm feels numb."},
            {"role": "assistant",
             "content": "Category: CRITICAL"},
            # Few-shot example 2: ROUTINE
            {"role": "user",
             "content": "Query: I need to renew my allergy pills prescription next month."},
            {"role": "assistant",
             "content": "Category: ROUTINE"},
            # Live target
            {"role": "user",
             "content": f"Query: {new_patient_query}"}
        ]
    )
    return response.choices[0].message.content

verdict = analyse_patient_urgency_few_shot(
    "My child has a mild fever but is laughing and playing.")
print(verdict)