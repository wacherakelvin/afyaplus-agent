# challenge_2_3_1_fallback.py (Solution)
import os
from langchain_community.document_loaders import TextLoader

def run_resilient_ingestion():
    primary_path = "./manual_data/operational_guidelines.txt"
    backup_path = "./manual_data/backup_guidelines.txt"

    print("--- Executing Resilient Ingestion Flow ---")
    try:
        print(f"Attempting primary load: {primary_path}")
        loader = TextLoader(primary_path)
        documents = loader.load()
        print("Primary document loaded successfully.")
        return documents
    except (FileNotFoundError, RuntimeError):
        print("WARNING: Primary file unavailable. Diverting to backup archive...")
        if os.path.exists(backup_path):
            loader = TextLoader(backup_path)
            documents = loader.load()
            print("Backup document loaded successfully.")
            return documents
        else:
            raise FileNotFoundError("CRITICAL ERROR: Both primary and backup compliance files are completely missing from the host environment directory.")

if __name__ == "__main__":
    try:
        run_resilient_ingestion()
    except Exception as e:
        print(f"System Safe Exit: {e}")