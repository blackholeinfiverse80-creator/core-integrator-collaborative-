# SCREENSHOTS — Evidence Index
**Sprint:** Production Deployment Validation  
**Date:** 2026-06-20  
**Instruction:** Capture these screenshots during live validation and place them in this folder.

---

## Required Screenshots

| Filename | What to Capture | How to Capture |
|----------|----------------|----------------|
| `01_running_services.png` | Terminal showing all 10 services started | Run `python start_all.py`, screenshot the output |
| `02_deployment_dashboard.png` | Control Plane dashboard at `/dashboard/executive` | `curl http://localhost:8009/dashboard/executive` or browser |
| `03_health_endpoints.png` | Pipeline health response | `curl http://localhost:8004/pipeline/health` |
| `04_pipeline_execution.png` | Successful pipeline execution with trace_id + artifact chain | `curl -X POST http://localhost:8004/pipeline/execute -d '{"prompt":"..."}'` |
| `05_replay_validation.png` | Replay response showing `source: bucket` and matching artifact chain | `curl http://localhost:8004/pipeline/replay/{trace_id}` |
| `06_observability_dashboard.png` | Metrics endpoint response | `curl http://localhost:8009/metrics` |
| `07_artifact_lineage.png` | Lineage endpoint showing A1→A4 chain | `curl http://localhost:8001/lineage/{instruction_id}` |
| `08_ttg_integration.png` | TTG pipeline execution response with `ttg_output` | `curl -X POST http://localhost:8004/pipeline/ttg -d '{...}'` |
| `09_ttv_integration.png` | TTV pipeline execution response with `ttv_output` | `curl -X POST http://localhost:8004/pipeline/ttv -d '{...}'` |
| `10_ai_content_platform.png` | AI Content Platform execution response | `curl -X POST http://localhost:8004/pipeline/content -d '{...}'` |

---

## Capture Commands (Copy-Paste Ready)

```bash
# 01 — Running services (run start_all.py and screenshot terminal)
python start_all.py

# 02 — Deployment dashboard
curl http://localhost:8009/dashboard/executive | python -m json.tool

# 03 — Health endpoints
curl http://localhost:8004/pipeline/health | python -m json.tool

# 04 — Pipeline execution
curl -X POST http://localhost:8004/pipeline/execute \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $AUTH_API_KEY" \
  -d '{"prompt": "Design a residential building for Mumbai"}' | python -m json.tool

# 05 — Replay validation (replace TRACE_ID with value from step 04)
curl http://localhost:8004/pipeline/replay/TRACE_ID \
  -H "X-API-Key: $AUTH_API_KEY" | python -m json.tool

# 06 — Observability dashboard
curl http://localhost:8009/metrics | python -m json.tool

# 07 — Artifact lineage (replace INSTRUCTION_ID)
curl http://localhost:8001/lineage/INSTRUCTION_ID \
  -H "X-API-Key: $AUTH_API_KEY" | python -m json.tool

# 08 — TTG integration
curl -X POST http://localhost:8004/pipeline/ttg \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $AUTH_API_KEY" \
  -d '{"game_type":"adventure","theme":"fantasy","difficulty":"medium","player_count":2,"description":"Create a dungeon crawler"}' | python -m json.tool

# 09 — TTV integration
curl -X POST http://localhost:8004/pipeline/ttv \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $AUTH_API_KEY" \
  -d '{"video_type":"tutorial","topic":"Python basics","duration":"5min","style":"animated","voice":"professional"}' | python -m json.tool

# 10 — AI Content Platform
curl -X POST http://localhost:8004/pipeline/content \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $AUTH_API_KEY" \
  -d '{"prompt": "Generate a content strategy for a tech startup"}' | python -m json.tool
```

---

## Note for Vinayak (Testing)

Place screenshot files directly in this `SCREENSHOTS/` folder with the filenames listed above.  
JSON responses can be saved as `.json` files alongside screenshots for audit trail.
