# AfyaPlus Triage Engine - Week 1 Capstone

## Prompt Engineering Iterations
- **V1 (Naive):** "Look at this message and tell me if it is an emergency." -> *Result: Returned conversational paragraphs that broke JSON parsing.*
- **V2 (Constrained):** Added role ("You are a triage nurse") and asked for JSON. -> *Result: Better, but occasionally output markdown fences (```json) or conversational fluff like "Here is your JSON".*
- **V3 (Defensive CoT + JSON Mode):** Added strict JSON mode, banned conversational fluff, and added Chain-of-Thought reasoning. -> *Result: 100% parseable, accurate medical reasoning.*

## Guardrails Added & Why
1. **Banned Conversational Fluff:** Prevented the model from adding "Sure!" so `json.loads()` never throws a `JSONDecodeError`.
2. **Chain-of-Thought Summary:** Forces the model to explain *why* it flagged an emergency, preventing silent hallucinations.
3. **Strict 4.0s Timeout:** Prevents the backend from hanging if the OpenAI API is slow, triggering the local Ollama fallback.

## Latency Comparison (Baseline)
*Tested with 1 patient query: "I am 8 months pregnant and I have a severe headache and my vision is blurry."*

| Model Provider | Model Name | Avg Latency | Cost | Notes |
|----------------|------------|-------------|------|-------|
| OpenAI (Cloud) | gpt-4o-mini | ~2.1 seconds | Paid | Requires internet & credits. |
| Ollama (Local) | llama3.2:1b | ~3.5 seconds | Free | Runs on CPU, 100% private. |

# Week 2 Capstone: Enterprise RAG Agent

## Orchestration Design
The system uses `LangGraph` (`create_react_agent`) for dynamic reasoning. It allows the agent to decide whether to call the LlamaIndex RAG tool (for policy questions) or the Math tool (for dosage calculations) based on the user's intent.

## Token Management
- **Chunking:** LlamaIndex uses `SentenceSplitter` with a chunk size of 256 and overlap of 30. This keeps clauses intact while avoiding massive token dumps.
- **Retrieval Depth:** Set to `similarity_top_k=2`. This ensures the agent only pulls the 2 most relevant policy paragraphs, saving context tokens.

## Compliance Guardrails (Kenya DPA 2019)
- **Data Minimization:** The `PrivacyMasker` class uses Regex to detect Kenyan phone numbers (`+254` or `07...`) and Emails.
- **Masking:** PII is swapped for `[PHONE_1]` and `[EMAIL_1]` *before* the LangChain agent sees it.
- **De-masking:** A secure local vault holds the real PII. Once the LLM responds, the text is de-masked locally before being shown to the user.