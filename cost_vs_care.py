import numpy as np

def simple_numpy_tokenizer(text):
    clean_text = text.lower().replace(".", "").replace("?", "").replace(",", "")
    tokens = clean_text.split()
    return np.array(tokens)

original_query = (
    "Hujambo, it is Juma. I am feeling very hot, my head hurts since yesterday, "
    "and I am coughing. I cannot go to the clinic because of the rain. What should I do?"
)

# TODO 1
original_tokens = simple_numpy_tokenizer(original_query)
original_count = len(original_tokens)

# TODO 2
summary = "Patient Juma: fever, headache since yesterday, cough, cannot reach clinic."

# TODO 3
summary_tokens = simple_numpy_tokenizer(summary)
summary_count = len(summary_tokens)

# TODO 4
saved = original_count - summary_count
pct_saved = 100 * saved / original_count

# TODO 5
tokens_per_month = saved * 1000 * 30

print(f"Original: {original_count} tokens")
print(f"Summary:  {summary_count} tokens")
print(f"Saved:    {saved} tokens ({pct_saved:.1f}%)")
print(f"Monthly:  {tokens_per_month:,} tokens saved")