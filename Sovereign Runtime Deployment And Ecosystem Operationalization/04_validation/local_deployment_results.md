# Local Deployment Results

**Classification:** live-service evidence (not simulation)  
**Generated:** 2026-07-07  
**Command:** `python run_comprehensive_live_tests.py`

## Service health (8/8 reachable, 7/8 healthy)

| Service | URL | Status | Notes |
|---|---|---|---|
| Prompt Runner | `:8003/health` | 200 OK | FastAPI service |
| Creator Core | `:8000/` | 200 OK | |
| BHIV Core | `:8001/system/health` | 429 during burst | Rate limiter active; use `/system/health` |
| Integration Bridge | `:8004/pipeline/health` | 200 OK | |
| Bucket | `:8005/bucket/stats` | 200 OK | 12 traces stored at test time |
| CET | `:8006/health` | 200 OK | |
| Sarathi | `:8007/health` | 200 OK | |
| Gate | `:8008/health` | 200 OK | |

## End-to-end pipeline results

| Product | Trace ID | Result | Replay | Bucket |
|---|---|---|---|---|
| TTG | `live_test_d61c664e3559` | PASS | 200 | 200 |
| TTV | `comp_ttv_bd10684a9d` | PASS | 200 | 200 |
| Gurukul | `comp_gurukul_8934d450a8` | FAIL (429 BHIV) | — | — |
| Simulation Runtime | `comp_simulation_runtime_40b176773f` | PASS | 200 | 200 |

### Sample successful artifact chain (TTV)

```
A1_instruction → A2_blueprint → A2b_contract → A2c_authority → A2d_gate → A3_execution → A4_result
```

Contract hash from CET included in deterministic hash computation.

## Before baseline (simulation — not live proof)

Command: `python full_tantra_flow_test.py`  
Trace: `inst_tantra_606bdd086cb4`  
Note: in-process simulation only; superseded by live traces above.

## Pass/fail summary

- **PASS:** All 8 services start and respond on localhost
- **PASS:** Live CET → Sarathi → Gate → BHIV pipeline demonstrated
- **PASS:** Replay and bucket retrieval for 3/4 products
- **FAIL:** Gurukul blocked by BHIV Core rate limit (429) during burst test window
- **PARTIAL:** Bucket stores 4 artifact types; contract/authority/gate not yet persisted separately

## Raw evidence

Full JSON: `05_evidence_packets/comprehensive_live_test_results.json`
