## evaluator.py
import nltk, string
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from rouge_score import rouge_scorer
from collections import Counter

# Download tokeniser data: 'punkt' for older NLTK, 'punkt_tab' for NLTK >= 3.9
for _pkg in ("punkt", "punkt_tab"):
    try:
        nltk.download(_pkg, quiet=True)
    except Exception:
        pass

def compute_bleu4(reference: str, hypothesis: str) -> float:
    """Computes BLEU-4: precision of 4-gram overlap."""
    ref_tokens = nltk.word_tokenize(reference.lower())
    hyp_tokens = nltk.word_tokenize(hypothesis.lower())
    smoother = SmoothingFunction().method1
    return sentence_bleu([ref_tokens], hyp_tokens,
                         weights=(0.25, 0.25, 0.25, 0.25),
                         smoothing_function=smoother)

def compute_rouge(reference: str, hypothesis: str) -> dict:
    """Computes ROUGE-1, ROUGE-2, and ROUGE-L F1 scores."""
    scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
    scores = scorer.score(reference, hypothesis)
    return {k: round(v.fmeasure, 4) for k, v in scores.items()}

def _normalise(text: str) -> list:
    """Strip punctuation for clean token comparison."""
    text = ''.join(ch for ch in text.lower() if ch not in string.punctuation)
    return text.split()

def compute_token_f1(reference: str, hypothesis: str) -> float:
    """Computes Token-level F1-score."""
    ref_tokens, hyp_tokens = _normalise(reference), _normalise(hypothesis)
    shared = sum((Counter(hyp_tokens) & Counter(ref_tokens)).values())
    if shared == 0: return 0.0
    precision = shared / len(hyp_tokens)
    recall    = shared / len(ref_tokens)
    return round(2 * precision * recall / (precision + recall), 4)

def evaluate_response(reference: str, hypothesis: str) -> dict:
    """Aggregates all metrics for a final audit report."""
    rouge = compute_rouge(reference, hypothesis)
    return {
        "bleu_4":   round(compute_bleu4(reference, hypothesis), 4),
        "rouge_1":  rouge['rouge1'],
        "rouge_2":  rouge['rouge2'],
        "rouge_l":  rouge['rougeL'],
        "token_f1": compute_token_f1(reference, hypothesis),
    }

if __name__ == "__main__":
    # Fully runnable, no API key required.
    reference  = ("The patient presents with a persistent dry cough lasting two weeks "
                  "and a low-grade fever, requiring referral to respiratory testing.")
    good_hyp   = ("The patient has had a dry cough for two weeks with a mild fever and "
                  "should be referred for respiratory testing.")
    weak_hyp   = "The patient has a cough and was told to see a doctor."

    for label, hyp in [("Accurate paraphrase", good_hyp), ("Vague summary", weak_hyp)]:
        print(label)
        for k, v in evaluate_response(reference, hyp).items():
            print(f"    {k:>9}: {v}")