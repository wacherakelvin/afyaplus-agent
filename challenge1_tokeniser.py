import numpy as np

def emergency_tokeniser(text):
    """Split text into tokens while preserving '!' as separate tokens."""
    text = text.lower()
    # Pad '!' with spaces so split() treats them as separate tokens
    text = text.replace("!", " ! ")
    # Remove other punctuation that shouldn't be tokens
    for punct in [".", "?", ",", ";", ":"]:
        text = text.replace(punct, "")
    # Split and wrap in NumPy array
    tokens = np.array(text.split())
    return tokens

samples = ["Help!!!", "I cannot breathe!", "My chest hurts."]
for s in samples:
    print(s, "->", emergency_tokeniser(s))