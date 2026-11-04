import numpy as np

def simple_numpy_tokenizer(text):
    clean_text = text.lower().replace(".", "").replace("?", "")
    tokens = clean_text.split()
    token_array = np.array(tokens)
    vocab, inverse_indices = np.unique(token_array, return_inverse=True)
    return token_array, vocab, inverse_indices

patient_query = "My chest hurts. Is it a heart attack?"
tokens, vocabulary, token_ids = simple_numpy_tokenizer(patient_query)

print("--- Tokenisation Results ---")
print(f"Original Text: {patient_query}")
print(f"Tokens: {tokens}")
print(f"Vocabulary: {vocabulary}")
print(f"Token IDs (Numerical Representation): {token_ids}")