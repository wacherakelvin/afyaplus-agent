# lab11_rag.py
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

load_dotenv()
embeddings = OpenAIEmbeddings()
vector_store = InMemoryVectorStore(embeddings)

vector_store.add_texts([
    "AfyaPlus reimburses staff travel within 30 days of an approved claim.",
    "Clinic equipment purchases above $500 require director sign-off."
])
retriever = vector_store.as_retriever()

prompt = ChatPromptTemplate.from_template(
    "Answer using only this context. If not found, say 'Information not found.'\n"
    "Context: {context}\nQuestion: {question}"
)
llm = ChatOpenAI(model="gpt-5.4-mini", temperature=0.0)

rag_chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt | llm | StrOutputParser()
)

print(rag_chain.invoke("How soon is staff travel reimbursed?"))