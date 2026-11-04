# lab10_multi_tool.py
import os
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent, AgentExecutor
from langchain_core.agents import AgentFinish
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

@tool
def get_clinic_stock_count(medication_name: str) -> str:
    """Returns the current stock count for a medication at the AfyaPlus clinic."""
    stock = {"amoxicillin": 120, "paracetamol": 540}
    return f"{stock.get(medication_name.lower(), 0)} units"

@tool
def calculate_shift_cost(hours: float, hourly_rate: float) -> str:
    """Calculates the total cost of a staff shift."""
    if hours < 0 or hourly_rate < 0:
        return "Error: hours and rate must be non-negative."
    return f"Shift cost: {hours * hourly_rate:.2f}"

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an AfyaPlus operations assistant."),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}")
])

tools = [get_clinic_stock_count, calculate_shift_cost]
agent = create_agent(llm, tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

try:
    result = executor.invoke({"input": "How much paracetamol do we have, and what is the cost of an 8-hour shift at 450 per hour?"})
    print(f"\n--- Final Answer ---")
    print(result.get("output", "No output returned"))
except Exception as e:
    print(f"Error running agent: {e}")
    import traceback
    traceback.print_exc()