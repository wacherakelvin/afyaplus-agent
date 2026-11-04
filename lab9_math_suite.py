import os
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langgraph.prebuilt import create_react_agent

load_dotenv()

@tool
def calculate_facility_utilization(active_beds: int, total_beds: int) -> str:
    """Calculates the capacity utilisation percentage for a clinic ward."""
    try:
        if total_beds <= 0:
            return "Error: total beds must be greater than zero."
        pct = (active_beds / total_beds) * 100
        return f"Utilisation: {pct:.1f}%"
    except Exception as e:
        return f"Error computing utilisation: {str(e)}"

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)
tools = [calculate_facility_utilization]

# Using the modern LangGraph agent we fixed earlier
agent = create_react_agent(llm, tools)

response = agent.invoke({"messages": [("human", "If 84 of our 100 beds are occupied, what is utilisation?")]})
print(f"Final Answer: {response['messages'][-1].content}")