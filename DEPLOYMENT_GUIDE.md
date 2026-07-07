# Deployment Guide

This guide explains how to deploy the BHIV Core-Integrator system locally, remotely, and in mixed environments.

## Local deployment

### Prerequisites

- Python 3.11 or higher
- `pip` installed
- Available ports: `8000`, `8001`, `8003`, `8004`, `8005`
- Optional: `uvicorn` for FastAPI services

### Install dependencies

```bash
python -m pip install -r requirements.txt
python -m pip install -r creator-core/Core-Integrator-Sprint-1.1/requirements.txt
```

### Startup order

1. `BHIV Bucket` — `python bhiv_bucket.py`
2. `Creator Core` — `cd creator-core/Core-Integrator-Sprint-1.1 && python main.py`
3. `BHIV Core` — `python main.py`
4. `Prompt Runner` — `python prompt-runner01/run_server.py`
5. `Integration Bridge` — `python integration_bridge.py`

Alternative startup commands:

```bash
python start_all.py
```

or:

```bash
python deploy_and_test.py
```

### Environment variables

Key variables used by the system:

- `PROMPT_RUNNER_URL` — Prompt Runner URL (default `http://127.0.0.1:8003`)
- `CREATOR_CORE_URL` — Creator Core URL (default `http://127.0.0.1:8000`)
- `BHIV_CORE_URL` — BHIV Core URL (default `http://127.0.0.1:8001`)
- `INTEGRATION_BRIDGE_URL` — Integration Bridge URL (default `http://127.0.0.1:8004`)
- `BUCKET_URL` — Bucket URL (default `http://127.0.0.1:8005`)
- `PORT` — service port override for Creator Core / BHIV Core
- `HOST` — host binding for services
- `DB_PATH` — path for BHIV Core database
- `STORAGE_PATH` — artifact folder for Bucket

Use `.env`, `.env.integration_bridge`, or service-local env files to override default values.

### Service ports

| Service | Default Port |
|---|---|
| Creator Core | 8000 |
| BHIV Core | 8001 |
| Prompt Runner | 8003 |
| Integration Bridge | 8004 |
| BHIV Bucket | 8005 |
| API Gateway | 8080 |

### Health checks

- Prompt Runner: `http://127.0.0.1:8003/health`
- Creator Core: `http://127.0.0.1:8000/`
- BHIV Core: `http://127.0.0.1:8001/`
- Integration Bridge: `http://127.0.0.1:8004/pipeline/health`
- BHIV Bucket: `http://127.0.0.1:8005/bucket/stats`

### Common local deployment failures

- Port collisions
- Missing Python dependencies
- Invalid or missing environment variables
- Prompt Runner stub not matching expected response shape
- Bucket storage folder permission issues

### Recovery procedures

1. Stop all services.
2. Verify env variables and ports.
3. Restart services in correct order.
4. Run `python test_services.py`.
5. Inspect logs and `bhiv_bucket/traces/`.

---

## Remote deployment

### Supported files

- `render.yaml` — Render deployment configuration
- `vercel.json` — Vercel deployment configuration
- `RENDER_DEPLOYMENT.md` — remote deployment notes
- `VERCEL_DEPLOYMENT.md` — Vercel-specific notes

### Remote deployment guidance

- Services can be deployed individually on remote hosts.
- Use HTTPS and secure endpoints.
- Set service URLs in remote environment variables.
- Ensure `PROMPT_RUNNER_URL`, `CREATOR_CORE_URL`, `BHIV_CORE_URL`, and `BUCKET_URL` match remote service locations.

### Remote environment variables

- `PROMPT_RUNNER_URL`
- `CREATOR_CORE_URL`
- `BHIV_CORE_URL`
- `INTEGRATION_BRIDGE_URL`
- `BUCKET_URL`
- `PORT`
- `HOST`
- `DB_PATH`
- `STORAGE_PATH`

### Remote deployment risks

- network latency
- inconsistent environment configuration
- missing or invalid service URL references
- unsecured HTTP endpoints

---

## Mixed deployment

Mixed deployment means some services run locally while others run remotely.

### Example configuration

- Local BHIV Core: `http://127.0.0.1:8001`
- Remote Creator Core: `https://creator.example.com`
- Remote Prompt Runner: `https://prompt-runner.example.com`
- Local Bucket: `http://127.0.0.1:8005`
- Local Integration Bridge: `http://127.0.0.1:8004`

### Requirements

- Remote endpoints must be reachable from the Integration Bridge process.
- All service URLs must be updated consistently.
- The prompt runner stub must be replaced if remote prompt generation is required.

### Common mixed deployment failures

- firewalls and routing issues
- mismatched protocols (`http` vs `https`)
- service URL misconfiguration
- version mismatch between services

---

## Dependencies

### Python dependencies

- `requirements.txt` — core dependencies
- `creator-core/Core-Integrator-Sprint-1.1/requirements.txt` — Creator Core dependencies
- `requirements-vercel.txt` — Vercel deployment dependencies

### Runtime dependencies

- `uvicorn`
- `fastapi`
- `pydantic`
- `requests`

## Deployment checklist

1. Install dependencies.
2. Validate environment variables.
3. Start Bucket.
4. Start Creator Core.
5. Start BHIV Core.
6. Start Prompt Runner.
7. Start Integration Bridge.
8. Run health checks.
9. Execute sample prompt.
10. Confirm artifact chain exists in Bucket.

## Troubleshooting

### Service unreachable

- Check process logs
- Confirm port listening
- Verify env configuration

### Data storage failure

- Validate `STORAGE_PATH`
- Check disk permissions and free space

### Bridge or pipeline errors

- Verify all upstream services are healthy
- Confirm `trace_id` propagation and artifact storage
- Inspect `bhiv_bucket/traces/` and service logs
