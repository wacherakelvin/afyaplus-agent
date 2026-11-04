# Prompt Iteration Comparison

| Evaluation Metric                      | V1 (Naive) | V2 (Constrained) | V3 (Defensive CoT) |
|----------------------------------------|------------|------------------|--------------------|
| Output Type (paragraph vs key-value)   | Paragraph  | Key-value        | Key-value + steps  |
| Preeclampsia Detection (flagged?)      | Often NO   | Usually YES      | Always YES         |
| Automation Readiness (regex-parseable) | NO         | YES              | YES                |
| Conversational Fluff (Yes/No)          | YES        | Maybe            | NO                 |

## Reflection
V3 prevents the model from agreeing with Chidinma's assumption to wait because
it must enumerate preeclampsia markers (persistent headache + sudden swelling)
BEFORE reaching FINAL STATUS. By the time the model has typed those markers,
the only logical conclusion is CRITICAL_URGENT. The defensive guardrails also
strip conversational fluff, making the output automation-ready.