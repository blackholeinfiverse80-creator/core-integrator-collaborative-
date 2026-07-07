# Local Deployment Results

## Before Baseline (simulation-based)

Command:
- `python full_tantra_flow_test.py`

Raw output excerpt:
- `Flow Complete: True`
- `Deterministic: True`
- `Trace ID Consistent: True`
- `Replay Hash Match: True`
- `trace_id: inst_tantra_606bdd086cb4`

This result is simulation-based and not live-service evidence.

## Live startup/health verification

Commands:
- `python start_all.py`
- `python test_services.py`

Observed:
- Initial runs failed due Windows cp1252 encoding issues in `start_all.py` (unicode arrow and emoji).
- After patching console symbols to ASCII, all 8 services report started, but orchestrator monitoring immediately marks all child services dead.
- `python test_services.py` can still intermittently report healthy checks when services are live.

## Drift / discrepancy note

- `start_all.py` was not stable on Windows due unicode console writes.
- Live pipeline execution is currently blocked by service lifecycle instability in orchestrator monitoring behavior and auth env propagation.
