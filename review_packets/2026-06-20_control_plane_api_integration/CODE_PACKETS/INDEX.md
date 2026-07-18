# CODE_PACKETS — Control Plane API Integration
**Date:** 2026-06-20

---

## Packet 1 — control_plane_service.py (CRITICAL)

| Field | Value |
|-------|-------|
| File path | `control_plane_service.py` |
| Purpose | All 7 Control Plane endpoints — the only file changed |
| Why modified | Removed `null` success_rate, added live aggregation, added `limit` params, added OpenAPI config, added `healthy` boolean, added `thresholds` to telemetry, added `summary` to runtime |
| Integration impact | Frontend can consume all endpoints with live data immediately |
| Review priority | CRITICAL |

**Key functions:**

| Function | Lines | Purpose |
|----------|-------|---------|
| `_aggregate_metrics()` | ~60 | Aggregates per-service snapshots into ecosystem totals |
| `_success_rate()` | ~65 | Computes `success_rate_pct` from total/error counts |
| `_insightflow_events()` | ~70 | Reads InsightFlow events via bucket API |
| `metrics()` | ~80 | `/metrics` — full ecosystem KPIs |
| `system_status()` | ~115 | `/system/status` — per-service health with `healthy` boolean |
| `dashboard_runtime()` | ~145 | `/dashboard/runtime` — runtime state + summary |
| `dashboard_operations()` | ~170 | `/dashboard/operations` — pipeline + bucket + replay |
| `dashboard_alerts()` | ~210 | `/dashboard/alerts` — merged ring buffer + bucket |
| `dashboard_telemetry()` | ~240 | `/dashboard/telemetry` — InsightFlow + per-trace + thresholds |

---

## No Other Files Modified

All data sources (`runtime_manager/state.py`, `spine/alert_generator.py`, `bhiv_bucket.py`, etc.) are unchanged.  
The control plane is a pure aggregation layer — it reads from other services and returns composed JSON.
