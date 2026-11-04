# lab2_4_1_ingestion.py

import os
from dotenv import load_dotenv
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
from llama_index.core.node_parser import SentenceSplitter

load_dotenv()

if not os.environ.get("OPENAI_API_KEY"):
   raise ValueError("CRITICAL: OPENAI_API_KEY is unassigned.")

print("--- Step 1: Loading raw assets via LlamaIndex ---")
reader = SimpleDirectoryReader("./data")
documents = reader.load_data()

print("--- Step 2: Segmenting text data using SentenceSplitter ---")
# Modern best practice: Using SentenceSplitter instead of the deprecated SimpleNodeParser
parser = SentenceSplitter(chunk_size=256, chunk_overlap=30)
nodes = parser.get_nodes_from_documents(documents)
print(f"Successfully generated {len(nodes)} structural document nodes.")

print("--- Step 3: Compiling VectorStore Index & Query Engine ---")
index = VectorStoreIndex(nodes)

# Challenge 18: Updated to retrieve top 2 nodes for multi-clause audits
base_query_engine = index.as_query_engine(similarity_top_k=2)

if __name__ == "__main__":
   query = "What are the data privacy rules and when do administrators run security audits?"
   print(f"\nExecuting Index Query: {query}")
   response = base_query_engine.query(query)
   print(f"LlamaIndex Output:\n{response}")