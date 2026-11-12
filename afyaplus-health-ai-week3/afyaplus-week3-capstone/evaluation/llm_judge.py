# llm_judge.py
import json
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

JUDGE_SYSTEM_PROMPT = """
You are an expert medical AI evaluation assistant for the AfyaPlus healthcare platform.
Evaluate the AI response on FOUR distinct dimensions, each scored from 1 to 5:

1. CORRECTNESS (1-5):  5=completely accurate, 3=minor gaps, 1=factually wrong or unsafe
2. GROUNDEDNESS (1-5): 5=fully supported by context, 3=minor unverified details, 1=hallucinated
3. RELEVANCE (1-5):    5=directly answers the query, 3=partially addresses it, 1=off-topic
4. HELPFULNESS (1-5):  5=immediately actionable for health workers, 3=vague, 1=unusable

Respond ONLY with valid JSON in this exact structure:
{
  "correctness": <1-5>,
  "groundedness": <1-5>,
  "relevance": <1-5>,
  "helpfulness": <1-5>,
  "overall": <average rounded to 1 decimal>,
  "reasoning": "<2-3 sentences explaining your assigned scores>"
}
"""

def llm_judge(question: str, reference: str, hypothesis: str,
              judge_model: str = "gpt-4o") -> dict:
    judge_llm = ChatOpenAI(model=judge_model, temperature=0, max_tokens=400)
    user_prompt = f"""
USER SYMPTOM QUERY: {question}
REFERENCE PROTOCOL:   {reference}
AI ASSISTANT RESPONSE: {hypothesis}
"""
    response = judge_llm.invoke([
        SystemMessage(content=JUDGE_SYSTEM_PROMPT),
        HumanMessage(content=user_prompt)
    ])
    raw = response.content.strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        import re
        m = re.search(r'\{.*\}', raw, re.DOTALL)
        return json.loads(m.group()) if m else {
            "correctness": 0, "groundedness": 0, "relevance": 0,
            "helpfulness": 0, "overall": 0, "reasoning": "JSON Parse failure"
        }

if __name__ == "__main__":
    # Runnable demo. Requires OPENAI_API_KEY in your environment or a loaded .env file.
    question  = "A patient reports a dry cough lasting two weeks and a low-grade fever. What should they do?"
    reference = ("Persistent cough beyond 14 days with fever warrants a mandatory referral "
                 "to respiratory clinical testing.")
    hypothesis = ("Since the cough has lasted two weeks and is accompanied by fever, the patient "
                  "should be referred for respiratory clinical testing.")
    scores = llm_judge(question, reference, hypothesis)
    for dim in ("correctness", "groundedness", "relevance", "helpfulness", "overall"):
        print(f"{dim:>13}: {scores.get(dim)}")
    print("reasoning:", scores.get("reasoning"))