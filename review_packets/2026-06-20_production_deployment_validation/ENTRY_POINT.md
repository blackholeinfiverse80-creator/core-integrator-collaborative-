# ENTRY_POINT.md
**Sprint:** Production Deployment Validation — Creator Core Ecosystem Integration  
**Date:** 2026-06-20  
**Reviewer:** Siddhesh Narkar (Product Integration Lead), Vinayak Tiwari (Testing)

---

## How to Start the System

### Option 1 — Single Command (Recommended)
```bash
cp .env.example .env
# Fill in: AUTH_API_KEY, AUTH_SECRET_KEY, GROQ_API_KEY
pip install -r requirements.txt
python start_all.py
```

### Option 2 — Docker Compose
```bash
cp .env.example .env
docker-compose up --build
```

### Option 3 — Manual (per service)
```bash
# Terminal 1 — Creator Core (port 8000)
cd creator-core/Core-Integrator-Sprint-1.1 && python main.py

# Terminal 2 — BHIV Core (port 8001)
uvicorn main:app --host 0.0.0.0 --port 8001

# Terminal 3 — Prompt Runner (port 8003)
python prompt-runner01/run_server.py

# Terminal 4 — Integration Bridge (port 8004)
uvicorn integration_bridge_v2:app --host 0.0.0.0 --port 8004

# Terminal 5 — BHIV Bucket (port 8005)
uvicorn bhiv_bucket:bucket_app --host 0.0.0.0 --port 8005

# Terminal 6 — Runtime Manager (all remaining services)
python -m runtime_manager
```

---

## Service Port Map

| Service            | Port | Health Endpoint              |
|--------------------|------|------------------------------|
| Creator Core       | 8000 | `GET /`                      |
| BHIV Core          | 8001 | `GET /system/health`         |
| Prompt Runner      | 8003 | `GET /health`                |
| Integration Bridge | 8004 | `GET /pipeline/health`       |
| BHIV Bucket        | 8005 | `GET /bucket/stats`          |
| CET Service        | 8006 | `GET /health`                |
| Sarathi Service    | 8007 | `GET /health`                |
| Gate Service       | 8008 | `GET /health`                |
| Control Plane      | 8009 | `GET /system/status`         |
| Telemetry Service  | 8010 | `GET /health`                |

---

## Minimum Required Environment Variables

```env
AUTH_ENABLED=true
AUTH_API_KEY=<your-api-key>
AUTH_SECRET_KEY=<your-secret-32-chars>
GROQ_API_KEY=<your-groq-key>
PYTHONPATH=.:./src:./creator-core/Core-Integrator-Sprint-1.1
USE_MONGODB=false
```

---

## Validate Everything is Running

```bash
# Pipeline health (all components)
curl http://localhost:8004/pipeline/health

# BHIV Core health
curl http://localhost:8001/system/health

# Control Plane status
curl http://localhost:8009/system/status

# Run full test suite
python -m pytest tests/ -v
```

---

## Cross-Product Integration Entry Points

| Product              | Endpoint                        | Method |
|----------------------|---------------------------------|--------|
| TTG                  | `POST /pipeline/ttg`            | POST   |
| TTV                  | `POST /pipeline/ttv`            | POST   |
| AI Content Platform  | `POST /pipeline/execute`        | POST   |
| Replay               | `GET /pipeline/replay/{trace_id}` | GET  |
| Lineage              | `GET /lineage/{instruction_id}` | GET    |
