# CODE_PACKETS — Review Index
**Sprint:** Production Deployment Validation  
**Date:** 2026-06-20  
**Instruction:** Reviewers should inspect only the files listed here unless deeper investigation is required.

---

## Packet 1 — Integration Bridge (CRITICAL)

| Field | Value |
|-------|-------|
| File path | `integration_bridge.py` |
| Purpose | Full pipeline orchestrator — routes all product requests through Prompt Runner → Creator Core → CET → Sarathi → Gate → BHIV Core → Bucket |
| Why modified | Added `/pipeline/ttg`, `/pipeline/ttv`, `/pipeline/content` endpoints to enable cross-product runtime consumption |
| Integration impact | TTG, TTV, and AI Content Platform now consume Creator Core runtime through this bridge |
| Review priority | CRITICAL |

**New endpoints added:**
- `POST /pipeline/ttg` — TTG product integration via TANTRA bridge
- `POST /pipeline/ttv` — TTV product integration via TANTRA bridge
- `POST /pipeline/content` — AI Content Platform integration
- `GET /pipeline/ttg/health` — TTG boundary validation
- `GET /pipeline/ttv/health` — TTV boundary validation

---

## Packet 2 — TANTRA Bridge (HIGH)

| Field | Value |
|-------|-------|
| File path | `src/adapters/tantra_bridge.py` |
| Purpose | Enforces TANTRA system boundaries — TTG/TTV cannot execute without going through the full pipeline |
| Why modified | Existing file — reviewed, no changes made. Boundary enforcement confirmed intact. |
| Integration impact | All TTG/TTV requests are forced through Prompt Runner → BHIV Core. No bypass possible. |
| Review priority | HIGH |

**Boundary enforcement verified:**
- `validate_system_boundaries()` checks all components before execution
- No direct Core calls from adapters
- Input normalizers are thin transformation layers only

---

## Packet 3 — TTG Adapter Pair (MEDIUM)

| Field | Value |
|-------|-------|
| File paths | `src/adapters/ttg_input_normalizer.py`, `src/adapters/ttg_output_adapter.py` |
| Purpose | Input: converts TTG game spec to unified prompt. Output: transforms Core result to TTG game format |
| Why modified | Existing files — reviewed, no changes made |
| Integration impact | TTG product receives structured `game_content`, `gameplay_structure`, `assets` from Core output |
| Review priority | MEDIUM |

---

## Packet 4 — TTV Adapter Pair (MEDIUM)

| Field | Value |
|-------|-------|
| File paths | `src/adapters/ttv_input_normalizer.py`, `src/adapters/ttv_output_adapter.py` |
| Purpose | Input: converts TTV video spec to unified prompt. Output: transforms Core result to TTV video format |
| Why modified | Existing files — reviewed, no changes made |
| Integration impact | TTV product receives structured `video_script`, `audio_requirements`, `visual_elements`, `timeline` |
| Review priority | MEDIUM |

---

## Packet 5 — API Integration Routers (MEDIUM)

| Field | Value |
|-------|-------|
| File paths | `api/ttg_integration.py`, `api/ttv_integration.py`, `api/ai_content_platform.py` |
| Purpose | Standalone FastAPI routers for each product — can be mounted independently |
| Why modified | New files created to provide product-specific integration entry points |
| Integration impact | Products can import and mount these routers independently of the main bridge |
| Review priority | MEDIUM |

---

## Packet 6 — Deployment Configuration (HIGH)

| Field | Value |
|-------|-------|
| File paths | `docker-compose.yml`, `Dockerfile`, `render.yaml`, `.env.example` |
| Purpose | Container orchestration and cloud deployment configuration |
| Why modified | Existing files — reviewed, no changes made |
| Integration impact | All 10 services deploy together via Docker Compose or individually via Render |
| Review priority | HIGH |

---

## Packet 7 — Runtime Manager (HIGH)

| Field | Value |
|-------|-------|
| File path | `runtime_manager/manager.py` |
| Purpose | Service lifecycle management — starts, monitors, and auto-restarts all 10 services |
| Why modified | Existing file — reviewed, no changes made |
| Integration impact | Ensures continuous operation; auto-restart on failure preserves trace continuity |
| Review priority | HIGH |

---

## Packet 8 — Observability Stack (MEDIUM)

| Field | Value |
|-------|-------|
| File paths | `src/utils/observability.py`, `spine/signal_generator.py`, `spine/alert_generator.py`, `telemetry_service.py` |
| Purpose | Distributed tracing, telemetry ingestion, signal generation, alert raising |
| Why modified | Existing files — reviewed, no changes made |
| Integration impact | Every request gets a trace_id; telemetry flows to dashboard via spine |
| Review priority | MEDIUM |

---

## Constitutional Boundary Confirmation

The following files were explicitly NOT modified:

| File | Reason |
|------|--------|
| `src/core/authority_engine.py` | Authority boundary frozen |
| `src/core/models.py` | Schema frozen |
| `src/core/execution_gate.py` | Constitutional boundary frozen |
| `src/utils/auth.py` | Auth unchanged |
| `src/utils/hmac_signer.py` | Security unchanged |
| `src/db/` | Database adapters unchanged |
