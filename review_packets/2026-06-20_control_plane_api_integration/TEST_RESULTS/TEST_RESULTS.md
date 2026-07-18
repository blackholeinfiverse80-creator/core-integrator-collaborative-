# TEST_RESULTS — Control Plane API Integration
**Date:** 2026-06-20

---

## How to Run

```bash
# Start control plane (if not already running via start_all.py)
python control_plane_service.py

# Or via runtime manager
python start_all.py
```

---

## Validation Commands (Copy-Paste)

```bash
BASE=http://localhost:8009

# TC-01: Health
curl -s $BASE/health | python -m json.tool

# TC-02: Metrics
curl -s $BASE/metrics | python -m json.tool

# TC-03: System Status
curl -s $BASE/system/status | python -m json.tool

# TC-04: Dashboard Runtime
curl -s $BASE/dashboard/runtime | python -m json.tool

# TC-05: Dashboard Operations
curl -s $BASE/dashboard/operations | python -m json.tool

# TC-06: Dashboard Alerts
curl -s "$BASE/dashboard/alerts?limit=25" | python -m json.tool

# TC-07: Dashboard Telemetry
curl -s "$BASE/dashboard/telemetry?limit=25" | python -m json.tool

# TC-08: OpenAPI JSON (for Pratik)
curl -s $BASE/openapi.json | python -m json.tool

# TC-09: Swagger UI (open in browser)
start http://localhost:8009/docs
```

---

## Acceptance Criteria

| # | Test | Expected | Pass Condition |
|---|------|----------|----------------|
| TC-01 | `GET /health` | `status: ok`, `uptime_seconds > 0` | `uptime_seconds` is a live float |
| TC-02 | `GET /metrics` | `success_rate_pct` is a float, not null | `success_rate_pct >= 0.0` |
| TC-02 | `GET /metrics` | `services.healthy` is an integer | `>= 0` |
| TC-02 | `GET /metrics` | `latency_ms.p50` and `p95` are floats | `>= 0.0` |
| TC-03 | `GET /system/status` | Each service has `healthy: true/false` | Boolean present on all services |
| TC-03 | `GET /system/status` | `overall_status` is `ok` or `degraded` | Not null, not empty |
| TC-04 | `GET /dashboard/runtime` | `summary.total == 10` | Matches service count |
| TC-04 | `GET /dashboard/runtime` | `services` has 10 entries | All services present |
| TC-05 | `GET /dashboard/operations` | `pipeline.total_traces >= 0` | Integer, not null |
| TC-05 | `GET /dashboard/operations` | `pipeline.artifacts_by_type` has all 9 types | All artifact types present |
| TC-06 | `GET /dashboard/alerts` | `total_alerts >= 0` | Integer |
| TC-06 | `GET /dashboard/alerts?limit=10` | `alerts` array length <= 10 | Limit respected |
| TC-06 | `GET /dashboard/alerts` | `by_severity` is a dict | Not null |
| TC-07 | `GET /dashboard/telemetry` | `classification_breakdown` has nominal/warning/critical | All 3 keys present |
| TC-07 | `GET /dashboard/telemetry` | `thresholds` has 4 metrics | Not empty |
| TC-07 | `GET /dashboard/telemetry` | `insightflow.by_component` is a dict | Not null |
| TC-08 | `GET /openapi.json` | Valid OpenAPI 3.x JSON | `openapi` field present |
| TC-09 | `GET /docs` | Swagger UI loads | HTTP 200 |

---

## No Mock Data Verification

Run this check — every field must be live:

```bash
# success_rate_pct must NOT be null
curl -s http://localhost:8009/metrics | python -c "
import sys, json
d = json.load(sys.stdin)
sr = d['requests']['success_rate_pct']
assert sr is not None, 'success_rate_pct is null!'
assert isinstance(sr, float), f'success_rate_pct is not float: {sr}'
print(f'PASS: success_rate_pct = {sr}')
"

# healthy boolean must be present on every service
curl -s http://localhost:8009/system/status | python -c "
import sys, json
d = json.load(sys.stdin)
for name, svc in d['services'].items():
    assert 'healthy' in svc, f'Missing healthy on {name}'
    assert isinstance(svc['healthy'], bool), f'healthy not bool on {name}'
print(f'PASS: healthy boolean present on all {len(d[\"services\"])} services')
"

# thresholds must be present in telemetry
curl -s http://localhost:8009/dashboard/telemetry | python -c "
import sys, json
d = json.load(sys.stdin)
assert d['thresholds'], 'thresholds is empty!'
print(f'PASS: thresholds = {list(d[\"thresholds\"].keys())}')
"
```
