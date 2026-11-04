import numpy as np
from collections import Counter

def predict_next_token(context, temperature=1.0):
    probs = {
        "and": 0.3, "with": 0.25, "recommend": 0.2,
        "suggesting": 0.15, "indicating": 0.1
    }
    tokens = list(probs.keys())
    weights = np.array(list(probs.values()))
    scaled = weights ** (1.0 / temperature)
    scaled = scaled / scaled.sum()
    return np.random.choice(tokens, p=scaled)

temperatures = [0.1, 0.5, 1.0, 2.0]
num_trials = 1000

for temp in temperatures:
    picks = [predict_next_token("patient has fever", temperature=temp)
             for _ in range(num_trials)]
    counts = Counter(picks)

    print(f"\n=== Temperature = {temp} ===")
    for token in ["and", "with", "recommend", "suggesting", "indicating"]:
        count = counts.get(token, 0)
        pct = 100 * count / num_trials
        print(f"  {token:<12} {count:>4} ({pct:5.1f}%)")