# EXECUTION_FLOW.md
**Sprint:** Production Deployment Validation  
**Date:** 2026-06-20

---

## Full Pipeline Execution Flow

```
User / Product (TTG / TTV / AI Content Platform)
        │
        ▼
Integration Bridge (port 8004)
  POST /pipeline/execute  |  POST /pipeline/ttg  |  POST /pipeline/ttv
        │
        ▼ Phase 1
Prompt Runner (port 8003)
  POST /generate
  → Converts raw prompt into structured instruction (JSON)
  → Assigns instruction_id, intent, topic, tasks
        │
        ▼ Phase 2
Creator Core (port 8000)
  POST /creator-core/generate-blueprint
  → Receives structured instruction
  → Generates Blueprint Envelope (A2)
  → Blueprint contains: payload, target_product, schema_version
        │
        ▼ Phase 3
BHIV Core (port 8001)
  POST /core
  → Receives blueprint
  → Routes through Gateway → RoutingEngine → Agent (creator/finance/education/video)
  → Wraps result in ExecutionEnvelope with input_hash, output_hash, semantic_hash
  → Stores lineage via LineageManager
        │
        ▼ Phase 4
BHIV Bucket (port 8005)
  POST /bucket/store  (called for each artifact A1→A4)
  → Stores: instruction, blueprint, execution, result
  → Indexed by trace_id and artifact_id
        │
        ▼ Phase 5
Integration Bridge assembles final result
  → Returns: trace_id, artifact_chain (A1→A4), pipeline_result, deterministic_hash
        │
        ▼
Product-Specific Output Adapter (TTG / TTV)
  → TTGOutputAdapter: transforms to game_content, gameplay_structure, assets
  → TTVOutputAdapter: transforms to video_script, audio_requirements, visual_elements
```

---

## Artifact Chain (A1 → A4)

| Artifact | ID Prefix     | Stored By       | Content                          |
|----------|---------------|-----------------|----------------------------------|
| A1       | `instruction_` | Integration Bridge | Raw prompt → structured instruction |
| A2       | `blueprint_`   | Integration Bridge | Blueprint envelope from Creator Core |
| A3       | `execution_`   | Integration Bridge | Execution result from BHIV Core  |
| A4       | `result_`      | Integration Bridge | Final assembled result           |

---

## Replay Flow

```
GET /pipeline/replay/{trace_id}
        │
        ▼
Integration Bridge → BHIV Bucket
  GET /bucket/trace/{trace_id}
        │
        ▼
Returns full artifact chain (A1→A4) from bucket
  → Validates deterministic_hash matches original
  → replay_timestamp recorded
  → source: "bucket" (live) or "local" (fallback)
```

---

## Recovery Flow

```
Service crash detected by RuntimeManager
        │
        ▼
RuntimeManager.monitor_services() detects unhealthy process
        │
        ▼
Auto-restart triggered (max 3 retries, backoff)
        │
        ▼
Health check re-validated on restart
        │
        ▼
Trace continuity preserved — in-flight traces resume from bucket artifacts
```

---

## TTG Integration Flow

```
TTG Product
  POST /pipeline/ttg  { game_type, theme, difficulty, player_count, description }
        │
        ▼
TANTRAIntegrationBridge.process_ttg_request()
  → TTGInputNormalizer.normalize() → unified prompt string
  → _execute_pipeline() → Prompt Runner → BHIV Core
  → TTGOutputAdapter.transform() → game_content, gameplay_structure, assets
        │
        ▼
TTG receives: { status, product:"ttg", trace_id, ttg_output, artifact_chain }
```

---

## TTV Integration Flow

```
TTV Product
  POST /pipeline/ttv  { video_type, topic, duration, style, voice, description }
        │
        ▼
TANTRAIntegrationBridge.process_ttv_request()
  → TTVInputNormalizer.normalize() → unified prompt string
  → _execute_pipeline() → Prompt Runner → BHIV Core
  → TTVOutputAdapter.transform() → video_script, audio_requirements, visual_elements
        │
        ▼
TTV receives: { status, product:"ttv", trace_id, ttv_output, artifact_chain }
```

---

## AI Content Platform Flow

```
AI Content Platform
  POST /pipeline/execute  { prompt: "..." }
        │
        ▼
BHIVIntegrationBridge.process_full_pipeline()
  → Full 4-phase pipeline (Prompt Runner → Creator Core → BHIV Core → Bucket)
        │
        ▼
Returns: { status, trace_id, artifact_chain, pipeline_result, timestamp }
```

---

## Observability Flow

```
Every request → observability_middleware (main.py)
  → new_trace_id() assigned
  → Request logged with trace_id, method, path, duration

Telemetry Service (port 8010)
  → Receives telemetry events
  → Validates via spine/telemetry_schema.py
  → Generates signals via spine/signal_generator.py
  → Raises alerts via spine/alert_generator.py
  → Dashboard APIs on Control Plane (port 8009): /dashboard/executive, /metrics, /health
```
