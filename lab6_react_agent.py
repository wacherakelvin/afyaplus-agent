# lab6_react_agent.py (Updated for 2024/2025 packages)
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent # Modern replacement for AgentExecutor

load_dotenv()

@tool
def get_clinic_stock_count(medication_name: str) -> str:
    """Returns current stock for a medication at the AfyaPlus clinic."""
    stock = {"amoxicillin": 120, "paracetamol": 540}
    return f"{stock.get(medication_name.lower(), 0)} units"

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)
tools = [get_clinic_stock_count]

# Create the agent using the modern LangGraph API
agent = create_react_agent(llm, tools)

# Invoke it
response = agent.invoke({"messages": [("human", "Do we have enough amoxicillin in stock?")]})
print(response["messages"][-1].content)