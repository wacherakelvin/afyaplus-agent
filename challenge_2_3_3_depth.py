# challenge_2_3_3_depth.py
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

def run_deep_vector_retrieval():
    loader = TextLoader("./manual_data/operational_guidelines.txt")
    chunks = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=20).split_documents(loader.load())
    vector_store = Chroma.from_documents(chunks, OpenAIEmbeddings(model="text-embedding-3-small"))

    # TODO: Step 1 - Configure as_retriever with search_kwargs targeting k=3
    retriever = None

    # TODO: Step 2 - Invoke with a target query
    # TODO: Step 3 - Iterate through the match collection and print each item
    pass

if __name__ == "__main__":
    run_deep_vector_retrieval()
