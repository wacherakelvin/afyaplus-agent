import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()
router_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0, max_tokens=1)

router_prompt = ChatPromptTemplate.from_template(
    "Classify the patient message as exactly one word, either CLINICAL or BILLING.\n"
    "Message: {message}\nClassification:"
)

router_chain = router_prompt | router_llm | StrOutputParser()

route = router_chain.invoke({"message": "I was charged twice for my last visit"}).strip().upper()
print(f"Routed to: {route}")