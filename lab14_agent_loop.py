# lab14_agent_loop.py
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent, AgentExecutor
from langchain_core.agents import AgentFinish
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool

load_dotenv()

@tool
def query_compliance_vault(question: str) -> str:
    """Use ONLY for AfyaPlus compliance-policy questions. Queries the grounded knowledge base."""
    # In the hybrid build this calls the LlamaIndex query engine; mocked here for the loop demo.
    return "Policy: procurement above $500 requires director sign-off."

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an AfyaPlus assistant. Use the compliance vault for policy questions."),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}")
])

tools = [query_compliance_vault]
agent = create_agent(llm, tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

try:
    result = executor.invoke({"input": "Do I need sign-off to buy a $900 centrifuge?"})
    print(f"\n--- Final Answer ---")
    print(result.get("output", "No output returned"))
except Exception as e:
    print(f"Error running agent: {e}")
    import traceback
    traceback.print_exc()