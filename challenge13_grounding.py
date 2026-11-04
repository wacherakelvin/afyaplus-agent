import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

load_dotenv()
store = InMemoryVectorStore(OpenAIEmbeddings())
store.add_texts(["AfyaPlus reimburses staff travel within 30 days of an approved claim."])
retriever = store.as_retriever()

prompt = ChatPromptTemplate.from_template(
    "Answer using ONLY the context. If the answer is not in it, reply exactly: "
    "Information not found.\nContext: {context}\nQuestion: {question}"
)

llm = ChatOpenAI(model="gpt-5.4-mini", temperature=0.0)
chain = ({"context": retriever, "question": RunnablePassthrough()} | prompt | llm | StrOutputParser())
print(chain.invoke("Best tourist beaches in Mombasa?"))   # -> Information not found.