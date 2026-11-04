# lab5_custom_tools.py
import os
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

load_dotenv()

@tool
def get_clinic_stock_count(medication_name: str) -> str:
    """Queries the AfyaPlus central inventory system for a specific drug.
    Use this tool whenever a patient asks if a medicine is physically available in the pharmacy.
    """
    # Mocking internal system database layer lookup
    inventory_db = {
        "paracetamol": "1,200 tablets available in Nairobi Hub.",
        "amoxicillin": "0 units left - currently backordered.",
        "antacid": "450 bottles in stock in Mombasa clinic."
    }
    normalized_name = medication_name.lower().strip()
    return inventory_db.get(normalized_name, f"Medication '{medication_name}' not found in database records.")

# Testing the structural tool properties that the LLM engine reads at runtime
print("--- Evaluating Tool Schema Metadata ---")
print(f"Tool Schema Name: {get_clinic_stock_count.name}")
print(f"Tool Schema Description: {get_clinic_stock_count.description}")
print(f"Direct Execution Output: {get_clinic_stock_count.invoke('amoxicillin')}\n")

# Bind the tool to the model
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)
llm_with_tools = llm.bind_tools([get_clinic_stock_count])

# Inspect tool_calls
response = llm_with_tools.invoke("Do we have any amoxicillin in stock right now?")
print("--- Inspecting Model's Tool Call Decision ---")
if response.tool_calls:
    for call in response.tool_calls:
        print(f"Tool requested: {call['name']}, Arguments: {call['args']}")
else:
    print(f"No tool call made. Model answered directly: {response.content}")