# CHANGED_FILES.md
**Sprint:** Production Deployment Validation  
**Date:** 2026-06-20  
**Scope:** Files created or modified to deliver cross-product runtime integration

---

## New Files Created This Sprint

| File | Purpose |
|------|---------|
| `review_packets/2026-06-20_production_deployment_validation/ENTRY_POINT.md` | Reviewer entry point — startup, ports, env vars |
| `review_packets/2026-06-20_production_deployment_validation/EXECUTION_FLOW.md` | Full pipeline and integration flow diagrams |
| `review_packets/2026-06-20_production_deployment_validation/CHANGED_FILES.md` | This file |
| `review_packets/2026-06-20_production_deployment_validation/API_PROOF.md` | API contract proof for all endpoints |
| `review_packets/2026-06-20_production_deployment_validation/DEPLOYMENT_PROOF.md` | Deployment evidence and validation |
| `review_packets/2026-06-20_production_deployment_validation/CODE_PACKETS/` | Reviewed code packets per component |
| `review_packets/2026-06-20_production_deployment_validation/TEST_RESULTS/` | Test execution results |
| `review_packets/2026-06-20_production_deployment_validation/LOGS/` | Runtime logs |
| `review_packets/2026-06-20_production_deployment_validation/SCREENSHOTS/` | Visual evidence placeholders |
| `api/ttg_integration.py` | TTG product integration FastAPI router |
| `api/ttv_integration.py` | TTV product integration FastAPI router |
| `api/ai_content_platform.py` | AI Content Platform integration router |

---

## Core Files (Existing — Reviewed, No Schema Changes)

| File | Role | Review Priority |
|------|------|----------------|
| `main.py` | BHIV Core entry point (port 8001) | HIGH |
| `integration_bridge_v2.py` | Full pipeline orchestrator (port 8004) | HIGH |
| `src/adapters/tantra_bridge.py` | TANTRA-compliant TTG/TTV bridge | HIGH |
| `src/adapters/ttg_input_normalizer.py` | TTG → unified prompt | MEDIUM |
| `src/adapters/ttv_input_normalizer.py` | TTV → unified prompt | MEDIUM |
| `src/adapters/ttg_output_adapter.py` | Core output → TTG format | MEDIUM |
| `src/adapters/ttv_output_adapter.py` | Core output → TTV format | MEDIUM |
| `src/core/gateway.py` | Request routing gateway | HIGH |
| `src/core/execution_envelope.py` | Deterministic hash + envelope | HIGH |
| `src/core/lineage_manager.py` | Artifact lineage tracking | HIGH |
| `src/core/replay_engine.py` | Replay from stored artifacts | HIGH |
| `src/utils/observability.py` | Trace ID + middleware | MEDIUM |
| `config/service_urls.py` | Service URL resolution | MEDIUM |
| `config/config_manager.py` | Config loading from env/yml | MEDIUM |
| `runtime_manager/manager.py` | Service lifecycle management | HIGH |
| `spine/signal_generator.py` | Telemetry signal generation | MEDIUM |
| `spine/alert_generator.py` | Alert generation from signals | MEDIUM |
| `docker-compose.yml` | Container orchestration | HIGH |
| `Dockerfile` | Container build definition | HIGH |
| `render.yaml` | Render.com deployment manifest | MEDIUM |
| `.env.example` | Environment variable template | HIGH |
| `requirements.txt` | Python dependencies | MEDIUM |

---

## Files NOT Modified (Boundary Preserved)

| File | Reason Not Modified |
|------|---------------------|
| `src/core/authority_engine.py` | Authority boundary — no changes per spec |
| `src/core/models.py` | Schema freeze — no changes per spec |
| `src/core/execution_gate.py` | Constitutional boundary — no changes per spec |
| `src/db/` | Database adapters — no schema changes |
| `src/utils/auth.py` | Auth unchanged — no authority changes |
| `src/utils/hmac_signer.py` | Security unchanged |

---

## Integration Impact Summary

- TTG and TTV now consume Creator Core runtime via TANTRA bridge
- AI Content Platform consumes via Integration Bridge `/pipeline/execute`
- All three products produce traceable artifact chains (A1→A4)
- Replay validated via `/pipeline/replay/{trace_id}`
- No constitutional boundary violations introduced
- No schema changes made
- No authority changes made
