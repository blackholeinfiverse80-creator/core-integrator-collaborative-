# SCREENSHOTS — Control Plane API Integration
**Date:** 2026-06-20

Capture these screenshots during live validation and place them in this folder.

---

## Required Screenshots

| Filename | Endpoint | Capture Command |
|----------|----------|----------------|
| `01_health.png` | `/health` | `curl -s http://localhost:8009/health \| python -m json.tool` |
| `02_metrics.png` | `/metrics` | `curl -s http://localhost:8009/metrics \| python -m json.tool` |
| `03_system_status.png` | `/system/status` | `curl -s http://localhost:8009/system/status \| python -m json.tool` |
| `04_dashboard_runtime.png` | `/dashboard/runtime` | `curl -s http://localhost:8009/dashboard/runtime \| python -m json.tool` |
| `05_dashboard_operations.png` | `/dashboard/operations` | `curl -s http://localhost:8009/dashboard/operations \| python -m json.tool` |
| `06_dashboard_alerts.png` | `/dashboard/alerts` | `curl -s "http://localhost:8009/dashboard/alerts?limit=25" \| python -m json.tool` |
| `07_dashboard_telemetry.png` | `/dashboard/telemetry` | `curl -s "http://localhost:8009/dashboard/telemetry?limit=25" \| python -m json.tool` |
| `08_swagger_ui.png` | `/docs` | Open `http://localhost:8009/docs` in browser |
| `09_running_service.png` | Terminal | Screenshot of `python control_plane_service.py` startup output |

---

## Key things to show in screenshots

- `02_metrics.png` — `success_rate_pct` must be a float (not null)
- `03_system_status.png` — `healthy: true/false` must be visible on each service
- `07_dashboard_telemetry.png` — `thresholds` block must be visible
- `08_swagger_ui.png` — All 7 endpoints must be visible in the Swagger UI
