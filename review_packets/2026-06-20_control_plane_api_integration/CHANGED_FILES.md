# CHANGED_FILES.md
**Sprint:** Control Plane API Integration  
**Date:** 2026-06-20  
**Task:** Wire all 6 frontend-required endpoints to live data. Remove placeholders.

---

## Modified Files

### `control_plane_service.py` — CRITICAL

| Field | Detail |
|-------|--------|
| File | `control_plane_service.py` |
| Port | 8009 |
| Why modified | All 6 required endpoints existed but had issues: `success_rate` returned `null`, `/dashboard/telemetry` had incomplete aggregation, no `limit` query param on alerts, no `healthy` boolean on services, no uptime from process start, no thresholds in telemetry response, no OpenAPI docs configured |
| What changed | Full rewrite — all endpoints now return production-ready JSON with live data. Added `limit` query param to `/dashboard/alerts` and `/dashboard/telemetry`. Added `success_rate_pct` computed from live metrics. Added `healthy` boolean per service. Added `thresholds` to telemetry response. Added `summary` block to runtime. Configured FastAPI with title, description, contact, `/docs`, `/redoc`, `/openapi.json`. |
| Integration impact | Frontend can now consume all 7 endpoints without mock data |
| Review priority | CRITICAL |

**Endpoints before → after:**

| Endpoint | Before | After |
|----------|--------|-------|
| `/health` | Missing `uptime_seconds` | Live process uptime added |
| `/metrics` | `success_rate: null` | `success_rate_pct` computed live |
| `/system/status` | No `healthy` boolean | `healthy: true/false` per service |
| `/dashboard/runtime` | Raw `read_status()` dump | Added `summary` block, `timestamp` |
| `/dashboard/operations` | Missing `success_rate_pct`, no recent traces | All fields live, `recent_traces` included |
| `/dashboard/alerts` | No `limit` param, no `by_status` | `limit` query param, `by_severity`, `by_status` |
| `/dashboard/telemetry` | Incomplete aggregation, no InsightFlow breakdown, no thresholds | Full InsightFlow event breakdown, `by_event_type`, `thresholds`, `limit` param |

---

## Files NOT Modified

| File | Reason |
|------|--------|
| `runtime_manager/state.py` | Data source — unchanged |
| `runtime_manager/metrics_middleware.py` | Data source — unchanged |
| `spine/alert_generator.py` | Data source — unchanged |
| `spine/signal_generator.py` | Data source — unchanged |
| `spine/thresholds.json` | Config — unchanged |
| `bhiv_bucket.py` | Data source — unchanged |
| `telemetry_service.py` | Data source — unchanged |
| `src/utils/insightflow.py` | Data source — unchanged |
| `src/core/models.py` | Schema freeze |
| `src/core/authority_engine.py` | Authority boundary |

---

## Data Sources Per Endpoint

| Endpoint | Data Sources |
|----------|-------------|
| `/health` | Process start time (`time.time()`) |
| `/metrics` | `runtime_manager/state.py`, `/internal/metrics-snapshot` (bridge + telemetry), bucket alert artifacts, `/replay/statistics` |
| `/system/status` | `runtime_manager/state.py`, bucket alert artifacts |
| `/dashboard/runtime` | `runtime_manager/state.py` |
| `/dashboard/operations` | `runtime_manager/state.py`, `/bucket/stats`, `/internal/metrics-snapshot`, `/replay/statistics`, `/bucket/traces` |
| `/dashboard/alerts` | `spine/alert_generator.get_alert_ring_buffer()`, bucket alert artifacts |
| `/dashboard/telemetry` | `/bucket/insightflow`, `/bucket/traces` + per-trace artifacts, `spine/thresholds.json` |
