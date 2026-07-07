# Runtime Architecture v2

## Execution policy

- **Gate authorizes; BHIV Core executes** — no double-execution
- Deterministic hash includes CET-issued `contract_hash`
- Artifact chain: A1 → A2 → A2b → A2c → A2d → A3 → A4

## Services (8)

| # | Service | Port | Role |
|---|---|---|---|
| 1 | Bucket | 8005 | Artifact persistence, trace index |
| 2 | Prompt Runner | 8003 | Prompt → instruction |
| 3 | Creator Core | 8000 | Instruction → blueprint |
| 4 | BHIV Core | 8001 | Module execution |
| 5 | CET | 8006 | Contract compilation |
| 6 | Sarathi | 8007 | Authority validation |
| 7 | Gate | 8008 | Execution authorization |
| 8 | Integration Bridge | 8004 | Pipeline orchestrator |

## Telemetry

- Integration Bridge → `bhiv_bucket/insightflow_events.jsonl`
- Creator Core → own telemetry writer

## Known gaps

- Bucket stores 4 artifact types; contract/authority/gate not separately persisted
- BHIV rate limiter can block burst testing (default 60/min)
- Remote/mixed deployment not validated in this sprint
