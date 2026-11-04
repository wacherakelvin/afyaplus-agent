# challenge_2_3_2_tuning.py (Solution)
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

def scale_chunk_geometry():
    print("--- Executing Chunk Hyperparameter Tuning ---")
    loader = TextLoader("./manual_data/operational_guidelines.txt")
    raw_docs = loader.load()

    # Re-configuring chunk limits for dense policy blocks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    tuned_chunks = text_splitter.split_documents(raw_docs)
    print(f"Tuned Configuration generated {len(tuned_chunks)} comprehensive data chunks.")

    # Print out verification blocks
    for idx, chunk in enumerate(tuned_chunks[:3]):
        print(f"\n--- Chunk Segment {idx + 1} ({len(chunk.page_content)} chars) ---")
        print(chunk.page_content)

if __name__ == "__main__":
    scale_chunk_geometry()