import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)

prompt = ChatPromptTemplate.from_template("Draft a one-sentence admin acknowledgement about: {topic}")
parser = StrOutputParser()

# The LCEL Pipe
chain = prompt | llm | parser 

print(chain.invoke({"topic": "a delayed lab result"}))