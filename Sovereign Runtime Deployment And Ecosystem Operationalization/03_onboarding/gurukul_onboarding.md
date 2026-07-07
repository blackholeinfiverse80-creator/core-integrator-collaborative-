# Gurukul Onboarding

**Trace ID:** `comp_gurukul_8934d450a8`  
**Status:** PARTIAL — adapter wired, live run blocked by BHIV 429

1. **Prompt Runner** — adapter normalizes gurukul prompts (wired)
2. **Creator Core** — not reached in failed run
3. **Core execution** — blocked at BHIV rate limit
4. **Bucket** — no complete trace
5. **InsightFlow** — prior gurukul events exist in jsonl from earlier attempts
6. **Replay** — not applicable for failed trace

Retry after service restart with elevated rate limits.
