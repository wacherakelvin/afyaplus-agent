# lab7_agent_memory.py
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory

load_dotenv()

@tool
def get_clinic_stock_count(medication_name: str) -> str:
    """Returns current stock for a medication at the AfyaPlus clinic."""
    return f"{ {'amoxicillin': 120}.get(medication_name.lower(), 0) } units"

llm = ChatOpenAI(model="gpt-5.4-mini", temperature=0.0)
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an AfyaPlus assistant. Remember the patient across turns."),
    ("placeholder", "{chat_history}"),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}")
])

tools = [get_clinic_stock_count]
agent = create_tool_calling_agent(llm, tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

store = {}
def get_session_history(session_id: str):
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

agent_with_memory = RunnableWithMessageHistory(
    executor, get_session_history,
    input_messages_key="input", history_messages_key="chat_history"
)

cfg = {"configurable": {"session_id": "patient-001"}}
agent_with_memory.invoke({"input": "My name is Achieng."}, cfg)
agent_with_memory.invoke({"input": "What is my name, and do we have amoxicillin?"}, cfg)