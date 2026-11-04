import numpy as np

embeddings = {
    "fever":     np.array([0.9, 0.0, 0.3]),
    "pain":      np.array([0.8, 0.1, 0.4]),
    "discharge": np.array([0.5, 0.5, 0.1]),
    "billing":   np.array([0.0, 0.9, 0.1]),
    "admit":     np.array([0.2, 0.8, 0.2]),
    # 'cough' is strongly clinical, barely administrative — sits near 'fever'
    "cough":     np.array([0.85, 0.05, 0.3]),
}

def cosine_similarity(word1, word2):
    vec1, vec2 = embeddings[word1], embeddings[word2]
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

fever_score   = cosine_similarity('cough', 'fever')
billing_score = cosine_similarity('cough', 'billing')

print(f"cough ↔ fever:   {fever_score:.4f}")
print(f"cough ↔ billing: {billing_score:.4f}")
print("✅ Cough clusters clinically" if fever_score > billing_score else "❌ Wrong side")