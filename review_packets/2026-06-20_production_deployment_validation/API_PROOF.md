# API_PROOF.md
**Sprint:** Production Deployment Validation  
**Date:** 2026-06-20  
**Purpose:** API contract proof for all integration endpoints

---

## 1. Integration Bridge — Full Pipeline

### `POST /pipeline/execute`
**Service:** Integration Bridge (port 8004)  
**Consumer:** AI Content Platform

**Request:**
```json
{
  "prompt": "Design a residential building for a 1000 sqft plot in Mumbai"
}
```

**Response:**
```json
{
  "status": "success",
  "trace_id": "trace_ae90e371d8da",
  "artifact_chain": {
    "trace_id": "trace_ae90e371d8da",
    "A1_instruction": "instruction_e2421518",
    "A2_blueprint": "blueprint_deda3253",
    "A3_execution": "execution_15e16a7f",
    "A4_result": "result_71570565"
  },
  "pipeline_result": {
    "original_prompt": "Design a residential building for a 1000 sqft plot in Mumbai",
    "pipeline_status": "completed",
    "deterministic_hash": "a1b2c3d4e5f67890"
  },
  "timestamp": "2026-06-20T10:00:00Z"
}
```

---

### `GET /pipeline/health`
**Service:** Integration Bridge (port 8004)

**Response:**
```json
{
  "pipeline_status": "healthy",
  "components": {
    "prompt_runner": { "status": "healthy", "code": 200 },
    "creator_core":  { "status": "healthy", "code": 200 },
    "bhiv_core":     { "status": "healthy", "code": 200 },
    "bucket":        { "status": "healthy", "code": 200 }
  },
  "service_urls": {
    "prompt_runner": "http://127.0.0.1:8003",
    "creator_core":  "http://127.0.0.1:8000",
    "bhiv_core":     "http://127.0.0.1:8001",
    "bucket":        "http://127.0.0.1:8005"
  },
  "timestamp": "2026-06-20T10:00:00Z"
}
```

---

### `GET /pipeline/replay/{trace_id}`
**Service:** Integration Bridge (port 8004)

**Request:** `GET /pipeline/replay/trace_ae90e371d8da`

**Response:**
```json
{
  "status": "success",
  "trace_id": "trace_ae90e371d8da",
  "artifact_chain": [
    { "artifact_id": "instruction_e2421518", "artifact_type": "instruction" },
    { "artifact_id": "blueprint_deda3253",   "artifact_type": "blueprint"   },
    { "artifact_id": "execution_15e16a7f",   "artifact_type": "execution"   },
    { "artifact_id": "result_71570565",      "artifact_type": "result"      }
  ],
  "replay_timestamp": "2026-06-20T10:05:00Z",
  "source": "bucket"
}
```

---

## 2. TTG Integration

### `POST /pipeline/ttg`
**Service:** Integration Bridge (port 8004)  
**Consumer:** TTG Product

**Request:**
```json
{
  "game_type": "adventure",
  "theme": "fantasy",
  "difficulty": "medium",
  "player_count": 2,
  "description": "Create a dungeon crawler game with puzzles"
}
```

**Response:**
```json
{
  "status": "success",
  "product": "ttg",
  "trace_id": "ttg_trace_1750420800.0",
  "ttg_output": {
    "game_content": {
      "title": "Dungeon Crawler",
      "description": "A fantasy dungeon crawler with puzzles",
      "genre": "adventure",
      "mechanics": [],
      "objectives": []
    },
    "gameplay_structure": {
      "levels": [],
      "progression": {},
      "difficulty_curve": "linear",
      "player_actions": []
    },
    "assets": {
      "characters": [],
      "environments": [],
      "items": [],
      "audio": {}
    },
    "metadata": {
      "execution_id": "exec_abc123",
      "trace_id": "ttg_trace_1750420800.0",
      "timestamp": "2026-06-20T10:00:00Z",
      "status": "success"
    }
  },
  "artifact_chain": {
    "execution_id": "exec_abc123",
    "input_hash": "sha256_input_hash",
    "output_hash": "sha256_output_hash",
    "semantic_hash": "sha256_semantic_hash",
    "timestamp": "2026-06-20T10:00:00Z"
  },
  "pipeline_metadata": {
    "original_input": { "game_type": "adventure", "theme": "fantasy" },
    "unified_prompt": "Create a dungeon crawler game with puzzles with fantasy theme for 2 player(s) at medium difficulty level",
    "timestamp": "2026-06-20T10:00:00Z"
  }
}
```

---

## 3. TTV Integration

### `POST /pipeline/ttv`
**Service:** Integration Bridge (port 8004)  
**Consumer:** TTV Product

**Request:**
```json
{
  "video_type": "tutorial",
  "topic": "Python programming basics",
  "duration": "5min",
  "style": "animated",
  "voice": "professional",
  "description": "Create a Python basics tutorial video for beginners"
}
```

**Response:**
```json
{
  "status": "success",
  "product": "ttv",
  "trace_id": "ttv_trace_1750420800.0",
  "ttv_output": {
    "video_script": {
      "title": "Python Basics Tutorial",
      "narration": "",
      "scenes": [],
      "dialogue": [],
      "captions": []
    },
    "audio_requirements": {
      "voice_type": "professional",
      "background_music": "none",
      "sound_effects": [],
      "audio_style": "standard"
    },
    "visual_elements": {
      "style": "animated",
      "animations": [],
      "transitions": [],
      "graphics": [],
      "text_overlays": []
    },
    "timeline": [
      { "timestamp": "0:00", "event": "intro" },
      { "timestamp": "0:05", "event": "main_content" },
      { "timestamp": "4:55", "event": "outro" }
    ],
    "metadata": {
      "execution_id": "exec_def456",
      "trace_id": "ttv_trace_1750420800.0",
      "timestamp": "2026-06-20T10:00:00Z",
      "status": "success"
    }
  },
  "artifact_chain": {
    "execution_id": "exec_def456",
    "input_hash": "sha256_input_hash",
    "output_hash": "sha256_output_hash",
    "semantic_hash": "sha256_semantic_hash",
    "timestamp": "2026-06-20T10:00:00Z"
  }
}
```

---

## 4. BHIV Core Endpoints

### `GET /system/health`
**Service:** BHIV Core (port 8001)

**Response:**
```json
{
  "status": "ok",
  "dependencies": {
    "database": "up",
    "gateway": "up",
    "noopur": "disabled",
    "video_service": "disabled"
  },
  "timestamp": "2026-06-20T10:00:00Z"
}
```

### `POST /replay/{instruction_id}`
**Service:** BHIV Core (port 8001)  
**Auth:** Required (`X-API-Key` header)

**Response:**
```json
{
  "status": "success",
  "instruction_id": "instr_abc123",
  "replay_result": { "status": "success", "result": {} },
  "determinism_validated": true
}
```

### `GET /lineage/{instruction_id}`
**Service:** BHIV Core (port 8001)  
**Auth:** Required

**Response:**
```json
{
  "instruction_id": "instr_abc123",
  "artifacts": ["blueprint_deda3253", "execution_15e16a7f", "result_71570565"],
  "trace_id": "trace_ae90e371d8da",
  "created_at": "2026-06-20T10:00:00Z"
}
```

---

## 5. BHIV Bucket Endpoints

### `GET /bucket/stats`
**Service:** BHIV Bucket (port 8005)

**Response:**
```json
{
  "total_artifacts": 4,
  "artifact_types": {
    "instruction": 1,
    "blueprint": 1,
    "execution": 1,
    "result": 1
  },
  "total_traces": 1
}
```

### `GET /bucket/trace/{trace_id}`
**Service:** BHIV Bucket (port 8005)

**Response:**
```json
{
  "trace_id": "trace_ae90e371d8da",
  "artifacts": [
    { "artifact_id": "instruction_e2421518", "artifact_type": "instruction", "data": {} },
    { "artifact_id": "blueprint_deda3253",   "artifact_type": "blueprint",   "data": {} },
    { "artifact_id": "execution_15e16a7f",   "artifact_type": "execution",   "data": {} },
    { "artifact_id": "result_71570565",      "artifact_type": "result",      "data": {} }
  ]
}
```

---

## 6. Control Plane / Observability

### `GET /system/status` (port 8009)
```json
{
  "status": "operational",
  "services": {
    "creator_core": "running",
    "bhiv_core": "running",
    "prompt_runner": "running",
    "integration_bridge": "running",
    "bucket": "running"
  },
  "timestamp": "2026-06-20T10:00:00Z"
}
```

### `GET /metrics` (port 8009)
```json
{
  "requests_total": 42,
  "requests_success": 40,
  "requests_failed": 2,
  "avg_latency_ms": 320,
  "replay_count": 5,
  "timestamp": "2026-06-20T10:00:00Z"
}
```

---

## Authentication

All protected endpoints require:
```
X-API-Key: <AUTH_API_KEY from .env>
```

Public endpoints (no auth): `/system/health`, `/`, `/pipeline/health`, `/bucket/stats`
