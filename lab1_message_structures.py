import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

load_dotenv()
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3) # Use gpt-4o-mini

messages = [
    SystemMessage(content="You are a Senior AI Engineer at AfyaPlus Health. Provide professional, safe guidance."),
    HumanMessage(content="Explain the difference between a chain and an agent.")
]
response = llm.invoke(messages)
print(response.content)