# Control Plane API — Endpoint Documentation for Pratik (Frontend)
**Service:** Control Plane  
**Base URL (local):** `http://localhost:8009`  
**Base URL (Docker):** `http://control-plane:8009`  
**Swagger UI:** `http://localhost:8009/docs`  
**ReDoc:** `http://localhost:8009/redoc`  
**OpenAPI JSON:** `http://localhost:8009/openapi.json`  
**Version:** 2.0.0  
**Auth:** No auth required on any of these endpoints (public dashboard APIs)

---

## Endpoint Summary

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/health` | Service liveness |
| GET | `/metrics` | Ecosystem-wide runtime metrics |
| GET | `/system/status` | Per-service health status |
| GET | `/dashboard/runtime` | Runtime Manager live state |
| GET | `/dashboard/operations` | Pipeline + bucket + replay stats |
| GET | `/dashboard/alerts` | Active and recent alerts |
| GET | `/dashboard/telemetry` | Telemetry events + signal classifications |

All endpoints return `Content-Type: application/json`.  
All endpoints include a `timestamp` field (ISO 8601 UTC).  
**No mock data. All fields are live.**

---

## GET /health

**Purpose:** Liveness probe — use for uptime monitoring.

```bash
curl http://localhost:8009/health
```

**Response:**
```json
{
  "status": "ok",
  "service": "control_plane",
  "uptime_seconds": 3963.619,
  "timestamp": "2026-06-20T10:00:00.000Z"
}
```

---

## GET /metrics

**Purpose:** Ecosystem-wide aggregated metrics for the main dashboard header/KPI cards.

```bash
curl http://localhost:8009/metrics
```

**Response:**
```json
{
  "timestamp": "2026-06-20T10:00:00.000Z",
  "uptime_seconds": 3963.619,
  "services": {
    "total": 10,
    "healthy": 9,
    "degraded": 1
  },
  "requests": {
    "total": 284,
    "errors": 3,
    "per_minute": 12,
    "error_rate_pct": 1.056,
    "success_rate_pct": 98.944
  },
  "latency_ms": {
    "p50": 142.5,
    "p95": 387.2
  },
  "alerts": {
    "active_count": 2,
    "by_severity": {
      "critical": 1,
      "high": 1
    }
  },
  "replay": {
    "total_replays": 18,
    "failed_replays": 0,
    "queue_depth": 0
  },
  "per_service_snapshots": {
    "integration_bridge": {
      "uptime_seconds": 3900.1,
      "total_requests": 210,
      "error_requests": 2,
      "error_rate_pct": 0.952,
      "requests_per_minute": 9,
      "latency_ms": { "p50": 138.0, "p95": 372.0 }
    },
    "telemetry": {
      "uptime_seconds": 3850.4,
      "total_requests": 74,
      "error_requests": 1,
      "error_rate_pct": 1.351,
      "requests_per_minute": 3,
      "latency_ms": { "p50": 147.0, "p95": 402.4 }
    }
  }
}
```

**Frontend usage:** KPI cards (healthy services, success rate, p95 latency, active alerts).

---

## GET /system/status

**Purpose:** Per-service health table — use for the services grid/table view.

```bash
curl http://localhost:8009/system/status
```

**Response:**
```json
{
  "timestamp": "2026-06-20T10:00:00.000Z",
  "overall_status": "degraded",
  "uptime_seconds": 3963.619,
  "shutting_down": false,
  "active_alerts": 2,
  "generated_at": "2026-07-08T10:51:05.694423+00:00",
  "services": {
    "prompt_runner": {
      "status": "healthy",
      "pid": 26472,
      "port": 8003,
      "restarts": 2,
      "last_restart_at": "2026-07-08T10:10:43.558000+00:00",
      "healthy": true
    },
    "creator_core": {
      "status": "healthy",
      "pid": 17232,
      "port": 8000,
      "restarts": 3,
      "last_restart_at": "2026-07-08T10:10:50.110945+00:00",
      "healthy": true
    },
    "bhiv_core": {
      "status": "CRASH_LOOPING",
      "pid": 25548,
      "port": 8001,
      "restarts": 2,
      "last_restart_at": "2026-07-08T09:56:56.721389+00:00",
      "healthy": false
    },
    "integration_bridge": {
      "status": "healthy",
      "pid": 21644,
      "port": 8004,
      "restarts": 2,
      "last_restart_at": "2026-07-08T10:11:22.369404+00:00",
      "healthy": true
    },
    "bucket": {
      "status": "healthy",
      "pid": 8244,
      "port": 8005,
      "restarts": 3,
      "last_restart_at": "2026-07-08T10:11:18.798706+00:00",
      "healthy": true
    },
    "cet": { "status": "healthy", "pid": 24420, "port": 8006, "restarts": 3, "last_restart_at": "2026-07-08T10:10:56.146932+00:00", "healthy": true },
    "sarathi": { "status": "healthy", "pid": 22756, "port": 8007, "restarts": 3, "last_restart_at": "2026-07-08T10:11:02.182525+00:00", "healthy": true },
    "gate": { "status": "healthy", "pid": 17312, "port": 8008, "restarts": 4, "last_restart_at": "2026-07-08T10:11:12.234979+00:00", "healthy": true },
    "control_plane": { "status": "healthy", "pid": 22100, "port": 8009, "restarts": 3, "last_restart_at": "2026-07-08T10:11:39.523642+00:00", "healthy": true },
    "telemetry": { "status": "healthy", "pid": 19340, "port": 8010, "restarts": 4, "last_restart_at": "2026-07-08T10:11:32.488000+00:00", "healthy": true }
  }
}
```

**Frontend usage:** Services health table. `overall_status` drives the top-level status badge.  
`healthy: true/false` is a convenience boolean for conditional styling.

---

## GET /dashboard/runtime

**Purpose:** Full Runtime Manager state — use for the runtime detail panel.

```bash
curl http://localhost:8009/dashboard/runtime
```

**Response:**
```json
{
  "timestamp": "2026-06-20T10:00:00.000Z",
  "generated_at": "2026-07-08T10:51:05.694423+00:00",
  "uptime_seconds": 3963.619,
  "shutting_down": false,
  "summary": {
    "total": 10,
    "healthy": 9,
    "degraded": 1
  },
  "services": {
    "prompt_runner": { "status": "healthy", "pid": 26472, "port": 8003, "restarts": 2, "last_restart_at": "..." },
    "creator_core":  { "status": "healthy", "pid": 17232, "port": 8000, "restarts": 3, "last_restart_at": "..." },
    "bhiv_core":     { "status": "CRASH_LOOPING", "pid": 25548, "port": 8001, "restarts": 2, "last_restart_at": "..." }
  }
}
```

**Frontend usage:** Runtime detail panel, service restart counters, PID display.

---

## GET /dashboard/operations

**Purpose:** Operational metrics — pipeline execution counts, bucket storage, replay stats.

```bash
curl http://localhost:8009/dashboard/operations
```

**Response:**
```json
{
  "timestamp": "2026-06-20T10:00:00.000Z",
  "pipeline": {
    "total_traces": 47,
    "total_artifacts": 188,
    "artifacts_by_type": {
      "telemetry": 47,
      "instruction": 47,
      "blueprint": 47,
      "contract": 47,
      "authority": 47,
      "gate": 47,
      "execution": 47,
      "result": 47,
      "alert": 3
    },
    "storage_size_mb": 0.84,
    "recent_traces": [
      { "trace_id": "trace_ae90e371d8da", "created_at": "2026-06-20T09:58:00Z", "artifact_count": 8 },
      { "trace_id": "trace_0a5c8b0a7e33", "created_at": "2026-06-20T09:55:00Z", "artifact_count": 7 }
    ]
  },
  "requests": {
    "total": 284,
    "errors": 3,
    "per_minute": 12,
    "error_rate_pct": 1.056,
    "success_rate_pct": 98.944
  },
  "latency_ms": { "p50": 142.5, "p95": 387.2 },
  "replay": { "total_replays": 18, "failed_replays": 0 },
  "runtime_services": { "...": "same as /system/status services" },
  "per_service_snapshots": { "...": "same as /metrics per_service_snapshots" }
}
```

**Frontend usage:** Operations dashboard — pipeline execution table, storage gauge, replay counter.

---

## GET /dashboard/alerts?limit=50

**Purpose:** Merged alert feed for the alerts panel.

**Query params:**
- `limit` (int, 1–200, default 50) — max alerts to return

```bash
curl "http://localhost:8009/dashboard/alerts?limit=25"
```

**Response:**
```json
{
  "timestamp": "2026-06-20T10:00:00.000Z",
  "total_alerts": 3,
  "by_severity": {
    "critical": 1,
    "high": 2
  },
  "by_status": {
    "critical": 1,
    "error": 2
  },
  "alerts": [
    {
      "alert_id": "alert_4f2a1b3c9d8e",
      "trace_id": "trace_ae90e371d8da",
      "severity": "critical",
      "reason": "Critical transformer_temp_c reading",
      "status": "critical",
      "raised_at": "2026-06-20T09:58:12.000Z",
      "signal": {
        "signal_id": "sig_7a3b2c1d4e5f",
        "metric": "transformer_temp_c",
        "value": 97.4,
        "unit": "celsius",
        "classification": "critical",
        "threshold_breached": true,
        "derived_at": "2026-06-20T09:58:11.000Z"
      },
      "decision_summary": {
        "gate_status": "ALLOWED",
        "execution_status": "success",
        "pipeline_status": "success"
      }
    }
  ]
}
```

**Frontend usage:** Alerts panel, severity badge counts, alert detail drawer.

---

## GET /dashboard/telemetry?limit=50

**Purpose:** Telemetry events, signal classifications, InsightFlow event stream.

**Query params:**
- `limit` (int, 1–200, default 50) — max per-trace records and InsightFlow events

```bash
curl "http://localhost:8009/dashboard/telemetry?limit=25"
```

**Response:**
```json
{
  "timestamp": "2026-06-20T10:00:00.000Z",
  "classification_breakdown": {
    "nominal": 38,
    "warning": 6,
    "critical": 3
  },
  "insightflow": {
    "total_events": 142,
    "by_component": {
      "integration_bridge": 47,
      "signal_generator": 47,
      "artifact_graph": 94,
      "core_integrator": 47
    },
    "by_event_type": {
      "instruction.received": 47,
      "signal.generated": 47,
      "artifact_graph.instruction": 47,
      "artifact_graph.result": 47
    },
    "recent_events": [
      {
        "insightflow_version": "1.0.0",
        "event_type": "signal.generated",
        "component": "signal_generator",
        "status": "success",
        "details": {
          "trace_id": "trace_ae90e371d8da",
          "classification": "critical"
        },
        "timestamp": "2026-06-20T09:58:11.000Z"
      }
    ]
  },
  "per_trace_telemetry": [
    {
      "trace_id": "trace_ae90e371d8da",
      "created_at": "2026-06-20T09:58:00Z",
      "telemetry": {
        "source_id": "substation-7",
        "metric": "transformer_temp_c",
        "value": 97.4,
        "unit": "celsius",
        "timestamp": "2026-06-20T09:58:00Z"
      },
      "signal": {
        "signal_id": "sig_7a3b2c1d4e5f",
        "metric": "transformer_temp_c",
        "value": 97.4,
        "classification": "critical",
        "threshold_breached": true
      },
      "alert": {
        "alert_id": "alert_4f2a1b3c9d8e",
        "severity": "critical",
        "reason": "Critical transformer_temp_c reading",
        "raised_at": "2026-06-20T09:58:12.000Z"
      }
    }
  ],
  "thresholds": {
    "grid_load_mw":       { "warning": 550.0, "critical": 700.0 },
    "voltage_v":          { "warning": 240.0, "critical": 260.0 },
    "transformer_temp_c": { "warning": 85.0,  "critical": 95.0  },
    "frequency_hz":       { "warning": 50.8,  "critical": 51.2  }
  }
}
```

**Frontend usage:** Telemetry chart, classification donut, InsightFlow event stream, threshold reference lines.

---

## Error Responses

All endpoints return standard HTTP error codes:

| Code | Meaning |
|------|---------|
| 200 | Success |
| 422 | Validation error (invalid query param) |
| 500 | Internal server error (upstream service unreachable) |

On upstream failure, the endpoint still returns 200 with empty/zero values rather than failing — the frontend should handle `0` counts gracefully.

---

## Polling Recommendations

| Endpoint | Suggested interval |
|----------|--------------------|
| `/health` | 30s |
| `/metrics` | 10s |
| `/system/status` | 10s |
| `/dashboard/runtime` | 5s |
| `/dashboard/operations` | 15s |
| `/dashboard/alerts` | 5s |
| `/dashboard/telemetry` | 10s |

---

## OpenAPI / Swagger

Interactive docs available at:
- Swagger UI: `http://localhost:8009/docs`
- ReDoc: `http://localhost:8009/redoc`
- Raw OpenAPI JSON: `http://localhost:8009/openapi.json`
