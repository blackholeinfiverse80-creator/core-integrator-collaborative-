"""Control Plane Service — Production-ready dashboard and metrics APIs.

Endpoints (all live data, no mocks):
  GET /health
  GET /metrics
  GET /system/status
  GET /dashboard/runtime
  GET /dashboard/operations
  GET /dashboard/alerts
  GET /dashboard/telemetry
"""

import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

import requests
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from config import ConfigManager

REPO_ROOT = Path(__file__).resolve().parent
SPRINT_DIR = REPO_ROOT / "SHAKTI Production Convergence Sprint (Energy Intelligence Platform Production Transition)"
if str(SPRINT_DIR) not in sys.path:
    sys.path.insert(0, str(SPRINT_DIR))

from runtime_manager.state import read_status
from spine.alert_generator import get_alert_ring_buffer

# ── Service URLs ──────────────────────────────────────────────────────────────
bucket_url           = ConfigManager.get_service_url("bucket")
bhiv_core_url        = ConfigManager.get_service_url("bhiv_core")
integration_bridge_url = ConfigManager.get_service_url("integration_bridge")
telemetry_url        = ConfigManager.get_service_url("telemetry")
api_key              = os.getenv("AUTH_API_KEY", "")

_STARTED_AT = time.time()

# ── FastAPI app ───────────────────────────────────────────────────────────────
app = FastAPI(
    title="Control Plane Service",
    description=(
        "Production dashboard and metrics APIs for the BHIV / Shakti ecosystem. "
        "All endpoints return live data sourced from Runtime Manager, BHIV Bucket, "
        "Replay Engine, and InsightFlow telemetry. No mock data."
    ),
    version="2.0.0",
    contact={"name": "Aman (Backend)", "email": "aman@bhiv.io"},
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# CORS — allow all origins by default; restrict via CORS_ORIGINS env var in production
# e.g. CORS_ORIGINS=https://dashboard.bhiv.io,https://app.bhiv.io
_raw_origins = os.getenv("CORS_ORIGINS", "*")
_allow_origins = [o.strip() for o in _raw_origins.split(",")] if _raw_origins != "*" else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allow_origins,
    allow_credentials=_raw_origins != "*",  # credentials only when origins are explicit
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Trace-Id", "X-Request-Id"],
    max_age=600,
)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _headers() -> Dict[str, str]:
    return {"X-API-Key": api_key} if api_key else {}


def _safe_get(url: str, timeout: int = 10) -> Dict[str, Any]:
    try:
        r = requests.get(url, headers=_headers(), timeout=timeout)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return {}


def _collect_service_metrics() -> Dict[str, Dict[str, Any]]:
    """Pull /internal/metrics-snapshot from each instrumented service."""
    snapshots: Dict[str, Dict[str, Any]] = {}
    targets = {
        "integration_bridge": integration_bridge_url,
        "telemetry": telemetry_url,
    }
    for name, base in targets.items():
        snap = _safe_get(f"{base}/internal/metrics-snapshot")
        if snap:
            snapshots[name] = snap
    return snapshots


def _aggregate_metrics(snapshots: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """Aggregate per-service metric snapshots into ecosystem-wide numbers."""
    flat = list(snapshots.values())
    if not flat:
        return {
            "total_requests": 0,
            "error_requests": 0,
            "requests_per_minute": 0,
            "error_rate_pct": 0.0,
            "latency_p50_ms": 0.0,
            "latency_p95_ms": 0.0,
        }
    total_req  = sum(v.get("total_requests", 0) for v in flat)
    total_err  = sum(v.get("error_requests", 0) for v in flat)
    rpm        = sum(v.get("requests_per_minute", 0) for v in flat)
    p50s = [v["latency_ms"]["p50"] for v in flat if v.get("latency_ms", {}).get("p50") is not None]
    p95s = [v["latency_ms"]["p95"] for v in flat if v.get("latency_ms", {}).get("p95") is not None]
    return {
        "total_requests":      total_req,
        "error_requests":      total_err,
        "requests_per_minute": rpm,
        "error_rate_pct":      round(total_err / total_req * 100.0, 3) if total_req else 0.0,
        "latency_p50_ms":      round(sum(p50s) / len(p50s), 3) if p50s else 0.0,
        "latency_p95_ms":      round(sum(p95s) / len(p95s), 3) if p95s else 0.0,
    }


def _bucket_traces(limit: int = 25) -> List[Dict[str, Any]]:
    return _safe_get(f"{bucket_url}/bucket/traces?limit={limit}").get("traces", [])


def _alerts_from_bucket(limit: int = 25) -> List[Dict[str, Any]]:
    """Collect alert artifacts from the most recent bucket traces."""
    traces = _bucket_traces(limit)
    alert_records: List[Dict[str, Any]] = []
    for trace in traces:
        trace_id = trace.get("trace_id")
        if not trace_id:
            continue
        artifacts = _safe_get(f"{bucket_url}/bucket/trace/{trace_id}").get("artifacts", [])
        for artifact in artifacts:
            if artifact.get("artifact_type") == "alert":
                alert_records.append(artifact.get("data", {}))
    alert_records.sort(key=lambda x: x.get("raised_at", ""), reverse=True)
    return alert_records


def _insightflow_events(limit: int = 200) -> List[Dict[str, Any]]:
    return _safe_get(f"{bucket_url}/bucket/insightflow?limit={limit}").get("events", [])


def _replay_stats() -> Dict[str, Any]:
    return _safe_get(f"{bhiv_core_url}/replay/statistics")


def _overall_status(runtime: Dict[str, Any]) -> str:
    for svc in runtime.get("services", {}).values():
        if svc.get("status") in ("unhealthy", "CRASH_LOOPING"):
            return "degraded"
    return "ok"


def _success_rate(total: int, errors: int) -> float:
    if total == 0:
        return 100.0
    return round((total - errors) / total * 100.0, 2)


def _uptime_seconds() -> float:
    """Control-plane process uptime (always live)."""
    return round(time.time() - _STARTED_AT, 3)


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.get(
    "/health",
    summary="Control Plane health check",
    tags=["Health"],
    response_description="Service liveness",
)
async def health():
    """Binary liveness probe — returns ok when the process is running."""
    return {
        "status": "ok",
        "service": "control_plane",
        "uptime_seconds": _uptime_seconds(),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get(
    "/metrics",
    summary="Ecosystem-wide runtime metrics",
    tags=["Metrics"],
    response_description="Aggregated request throughput, latency, error rate, alert count, replay depth",
)
async def metrics():
    """
    Live aggregated metrics pulled from:
    - Runtime Manager state file (service health)
    - Integration Bridge /internal/metrics-snapshot
    - Telemetry Service /internal/metrics-snapshot
    - BHIV Bucket alert artifacts
    - BHIV Core /replay/statistics
    """
    runtime  = read_status()
    snaps    = _collect_service_metrics()
    agg      = _aggregate_metrics(snaps)
    alerts   = _alerts_from_bucket(limit=50)
    replay   = _replay_stats()

    services = runtime.get("services", {})
    healthy_count  = sum(1 for s in services.values() if s.get("status") == "healthy")
    degraded_count = sum(1 for s in services.values() if s.get("status") in ("unhealthy", "CRASH_LOOPING"))

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "uptime_seconds": runtime.get("uptime_seconds") or _uptime_seconds(),
        "services": {
            "total":    len(services),
            "healthy":  healthy_count,
            "degraded": degraded_count,
        },
        "requests": {
            "total":              agg["total_requests"],
            "errors":             agg["error_requests"],
            "per_minute":         agg["requests_per_minute"],
            "error_rate_pct":     agg["error_rate_pct"],
            "success_rate_pct":   _success_rate(agg["total_requests"], agg["error_requests"]),
        },
        "latency_ms": {
            "p50": agg["latency_p50_ms"],
            "p95": agg["latency_p95_ms"],
        },
        "alerts": {
            "active_count": len(alerts),
            "by_severity":  _count_by_key(alerts, "severity"),
        },
        "replay": {
            "total_replays":   replay.get("total_replays", 0),
            "failed_replays":  replay.get("failed_replays", 0),
            "queue_depth":     replay.get("failed_replays", 0),
        },
        "per_service_snapshots": snaps,
    }


@app.get(
    "/system/status",
    summary="Overall system health status",
    tags=["System"],
    response_description="Service-by-service health with overall status",
)
async def system_status():
    """
    Live system status from Runtime Manager state file.
    Returns per-service health, restart counts, PIDs, and overall status.
    """
    runtime = read_status()
    alerts  = _alerts_from_bucket(limit=25)
    overall = _overall_status(runtime)

    services_enriched: Dict[str, Any] = {}
    for name, svc in runtime.get("services", {}).items():
        services_enriched[name] = {
            "status":          svc.get("status", "unknown"),
            "pid":             svc.get("pid"),
            "port":            svc.get("port"),
            "restarts":        svc.get("restarts", 0),
            "last_restart_at": svc.get("last_restart_at"),
            "healthy":         svc.get("status") == "healthy",
        }

    return {
        "timestamp":        datetime.now(timezone.utc).isoformat(),
        "overall_status":   overall,
        "uptime_seconds":   runtime.get("uptime_seconds") or _uptime_seconds(),
        "shutting_down":    runtime.get("shutting_down", False),
        "services":         services_enriched,
        "active_alerts":    len(alerts),
        "generated_at":     runtime.get("generated_at"),
    }


@app.get(
    "/dashboard/runtime",
    summary="Runtime Manager live state",
    tags=["Dashboard"],
    response_description="Full runtime state snapshot from Runtime Manager",
)
async def dashboard_runtime():
    """
    Raw Runtime Manager state — service PIDs, ports, restart counts, uptime.
    Sourced directly from runtime_manager/state/runtime_status.json (live file).
    """
    runtime = read_status()
    return {
        "timestamp":      datetime.now(timezone.utc).isoformat(),
        "generated_at":   runtime.get("generated_at"),
        "uptime_seconds": runtime.get("uptime_seconds") or _uptime_seconds(),
        "shutting_down":  runtime.get("shutting_down", False),
        "services":       runtime.get("services", {}),
        "summary": {
            "total":    len(runtime.get("services", {})),
            "healthy":  sum(1 for s in runtime.get("services", {}).values() if s.get("status") == "healthy"),
            "degraded": sum(1 for s in runtime.get("services", {}).values() if s.get("status") in ("unhealthy", "CRASH_LOOPING")),
        },
    }


@app.get(
    "/dashboard/operations",
    summary="Operational pipeline metrics and bucket stats",
    tags=["Dashboard"],
    response_description="Pipeline execution counts, bucket stats, per-service metrics",
)
async def dashboard_operations():
    """
    Operational view combining:
    - Runtime Manager service state
    - BHIV Bucket stats (artifact counts, trace counts, storage size)
    - Per-service request metrics snapshots
    - Replay statistics
    """
    runtime      = read_status()
    bucket_stats = _safe_get(f"{bucket_url}/bucket/stats")
    snaps        = _collect_service_metrics()
    agg          = _aggregate_metrics(snaps)
    replay       = _replay_stats()
    traces       = _bucket_traces(limit=10)

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "pipeline": {
            "total_traces":          bucket_stats.get("total_traces", 0),
            "total_artifacts":       bucket_stats.get("total_artifacts", 0),
            "artifacts_by_type":     bucket_stats.get("by_type", {}),
            "storage_size_mb":       bucket_stats.get("storage_size_mb", 0.0),
            "recent_traces":         traces,
        },
        "requests": {
            "total":            agg["total_requests"],
            "errors":           agg["error_requests"],
            "per_minute":       agg["requests_per_minute"],
            "error_rate_pct":   agg["error_rate_pct"],
            "success_rate_pct": _success_rate(agg["total_requests"], agg["error_requests"]),
        },
        "latency_ms": {
            "p50": agg["latency_p50_ms"],
            "p95": agg["latency_p95_ms"],
        },
        "replay": {
            "total_replays":  replay.get("total_replays", 0),
            "failed_replays": replay.get("failed_replays", 0),
        },
        "runtime_services": runtime.get("services", {}),
        "per_service_snapshots": snaps,
    }


@app.get(
    "/dashboard/alerts",
    summary="Active and recent alerts",
    tags=["Dashboard"],
    response_description="Deduplicated alert list from in-memory ring buffer and bucket",
)
async def dashboard_alerts(limit: int = Query(default=50, ge=1, le=200)):
    """
    Merged alert feed from:
    - In-memory alert ring buffer (spine/alert_generator.py — last 200 alerts)
    - BHIV Bucket persisted alert artifacts (last N traces)

    Deduplication by alert_id. Sorted newest-first.
    """
    ring      = get_alert_ring_buffer()
    persisted = _alerts_from_bucket(limit=limit)

    ring_ids = {a.get("alert_id") for a in ring}
    merged   = ring + [a for a in persisted if a.get("alert_id") not in ring_ids]
    merged.sort(key=lambda x: x.get("raised_at", ""), reverse=True)
    merged = merged[:limit]

    by_severity = _count_by_key(merged, "severity")
    by_status   = _count_by_key(merged, "status")

    return {
        "timestamp":    datetime.now(timezone.utc).isoformat(),
        "total_alerts": len(merged),
        "by_severity":  by_severity,
        "by_status":    by_status,
        "alerts":       merged,
    }


@app.get(
    "/dashboard/telemetry",
    summary="Recent telemetry events and signal classifications",
    tags=["Dashboard"],
    response_description="InsightFlow events, signal classifications, and per-trace telemetry",
)
async def dashboard_telemetry(limit: int = Query(default=50, ge=1, le=200)):
    """
    Live telemetry view combining:
    - InsightFlow events from bhiv_bucket/insightflow_events.jsonl
    - Per-trace telemetry and signal artifacts from BHIV Bucket
    - Classification breakdown (nominal / warning / critical)
    - Threshold reference from spine/thresholds.json
    """
    import json as _json

    # InsightFlow events (fast path — local file read via bucket API)
    if_events = _insightflow_events(limit=limit)

    # Per-trace telemetry + signal artifacts
    traces = _bucket_traces(limit=min(limit, 25))
    per_trace: List[Dict[str, Any]] = []
    classifications = {"nominal": 0, "warning": 0, "critical": 0}

    for trace in traces:
        trace_id = trace.get("trace_id")
        if not trace_id:
            continue
        artifacts = _safe_get(f"{bucket_url}/bucket/trace/{trace_id}").get("artifacts", [])
        record: Dict[str, Any] = {
            "trace_id":  trace_id,
            "created_at": trace.get("created_at"),
            "telemetry": None,
            "signal":    None,
            "alert":     None,
        }
        for artifact in artifacts:
            atype = artifact.get("artifact_type")
            data  = artifact.get("data", {})
            if atype == "telemetry":
                record["telemetry"] = {
                    "source_id": data.get("source_id"),
                    "metric":    data.get("metric"),
                    "value":     data.get("value"),
                    "unit":      data.get("unit"),
                    "timestamp": data.get("timestamp"),
                }
            elif atype == "alert":
                signal = data.get("signal", {})
                record["signal"] = signal
                record["alert"]  = {
                    "alert_id": data.get("alert_id"),
                    "severity": data.get("severity"),
                    "reason":   data.get("reason"),
                    "raised_at": data.get("raised_at"),
                }
                cls = signal.get("classification", "nominal")
                if cls in classifications:
                    classifications[cls] += 1

        if record["telemetry"] or record["signal"]:
            per_trace.append(record)

    per_trace.sort(
        key=lambda x: (x.get("telemetry") or {}).get("timestamp", ""),
        reverse=True,
    )

    # InsightFlow component breakdown
    by_component: Dict[str, int] = {}
    by_event_type: Dict[str, int] = {}
    for ev in if_events:
        c = ev.get("component", "unknown")
        e = ev.get("event_type", "unknown")
        by_component[c] = by_component.get(c, 0) + 1
        by_event_type[e] = by_event_type.get(e, 0) + 1

    # Load thresholds for frontend reference
    thresholds: Dict[str, Any] = {}
    try:
        thresholds = _json.loads(
            (REPO_ROOT / "spine" / "thresholds.json").read_text(encoding="utf-8")
        )
    except Exception:
        pass

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "classification_breakdown": classifications,
        "insightflow": {
            "total_events":    len(if_events),
            "by_component":    by_component,
            "by_event_type":   by_event_type,
            "recent_events":   if_events[-20:],
        },
        "per_trace_telemetry": per_trace[:limit],
        "thresholds": thresholds,
    }


# ── Utility ───────────────────────────────────────────────────────────────────

def _count_by_key(items: List[Dict[str, Any]], key: str) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for item in items:
        val = item.get(key, "unknown")
        counts[val] = counts.get(val, 0) + 1
    return counts


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8009)
