# Partial Failure Results

**Status:** PASS — BHIV rate limit failure handled  
**Generated:** 2026-07-07

## Scenario: BHIV Core rejects execution (429)

When BHIV Core rate limit is exceeded, Integration Bridge returns HTTP 500 with detail:

```json
{"detail": "429 Client Error: Too Many Requests for url: http://127.0.0.1:8001/core"}
```

Traces affected: `comp_ttg_bca6477faa`, `comp_gurukul_8934d450a8`

## Observed behavior

- Pipeline stops before A3 execution
- No false success returned
- Earlier artifacts (A1, A2, A2b–A2d) may exist in pipeline response but execution does not complete

## Mitigation applied

`core/service_orchestrator.py` now sets `RATE_LIMIT_IP_PER_MIN=10000` for local startup (requires service restart to take effect).

## Pass/fail

- **PASS:** Partial failure visible and does not corrupt completed traces
- **NOT RUN:** Bucket rejecting specific artifact type mid-chain
