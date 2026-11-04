# challenge8_depreciation.py
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain.agents import create_agent, AgentExecutor
from langchain_core.agents import AgentFinish
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

@tool
def calculate_asset_depreciation(initial_cost: float, salvage_value: float, useful_life_years: int) -> str:
    """Calculates annual straight-line depreciation for a clinic asset."""
    if useful_life_years <= 0:
        return "Error: useful life must be positive; division by zero is prohibited."
    annual = (initial_cost - salvage_value) / useful_life_years
    return f"Annual depreciation: {annual:.2f}"

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an AfyaPlus logistics assistant."),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}")
])

tools = [calculate_asset_depreciation]
agent = create_agent(llm, tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
try:
    result = executor.invoke({"input": "Yearly depreciation for a $5,000 server, $500 salvage, 5-year life?"})
    print(f"\n--- Final Answer ---")
    print(result.get("output", "No output returned"))
except Exception as e:
    print(f"Error running agent: {e}")
    import traceback
    traceback.print_exc()