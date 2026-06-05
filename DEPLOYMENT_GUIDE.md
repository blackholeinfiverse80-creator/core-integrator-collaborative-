# BHIV Deployment Guide

This guide explains how to deploy each BHIV service independently.

## Service Architecture

```
┌─────────────────┐
│  Prompt Runner  │ Port 8003 - Converts prompts to instructions
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Creator Core   │ Port 8000 - Generates blueprints
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   BHIV Core     │ Port 8001 - Executes blueprints
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│     Bucket      │ Port 8005 - Stores artifacts
└─────────────────┘

┌─────────────────┐
│ Integration     │ Port 8004 - Orchestrates all services
│ Bridge          │
└─────────────────┘
```

## Independent Deployment

Each service can be deployed separately on different servers/ports.

### 1. Environment Variables for Each Service

Create a `.env` file for each service:

#### Prompt Runner (.env)
```bash
# Prompt Runner Configuration
GROQ_API_KEY=your_groq_api_key_here
PORT=8003

# Optional: Creator Core URL (if calling /run endpoint)
CREATOR_CORE_URL=http://your-creator-core-host:8000
```

#### Creator Core (.env)
```bash
# Creator Core Configuration
GROQ_API_KEY=your_groq_api_key_here
PORT=8000
```

#### BHIV Core (.env)
```bash
# BHIV Core Configuration
PORT=8001

# Database (choose one)
USE_MONGODB=false
DB_PATH=data/context.db

# OR for MongoDB
# USE_MONGODB=true
# MONGODB_CONNECTION_STRING=mongodb://your-mongodb-host:27017
# MONGODB_DATABASE_NAME=bhiv_production

# Optional: Noopur Integration
INTEGRATOR_USE_NOOPUR=false
```

#### Bucket (.env)
```bash
# Bucket Configuration
PORT=8005
STORAGE_PATH=data/artifacts
```

#### Integration Bridge (.env)
```bash
# Integration Bridge Configuration
PORT=8004

# Service URLs - UPDATE THESE FOR YOUR DEPLOYMENT
PROMPT_RUNNER_URL=http://your-prompt-runner-host:8003
CREATOR_CORE_URL=http://your-creator-core-host:8000
BHIV_CORE_URL=http://your-bhiv-core-host:8001
BUCKET_URL=http://your-bucket-host:8005
```

### 2. Deploy Individual Services

#### Deploy Prompt Runner
```bash
# Prompt Runner is deployed separately outside this repository.
# Configure PROMPT_RUNNER_URL to point to your external Prompt Runner host.
```

#### Deploy Creator Core
```bash
cd creator-core/Core-Integrator-Sprint-1.1
pip install -r requirements.txt
python main.py
```

#### Deploy BHIV Core
```bash
pip install -r requirements.txt
python main.py
```

#### Deploy Bucket
```bash
python bhiv_bucket.py
```

#### Deploy Integration Bridge
1. Copy the example env file:
```bash
# Linux / macOS
cp .env.integration_bridge.example .env.integration_bridge

# Windows PowerShell
Copy-Item .env.integration_bridge.example .env.integration_bridge
```
2. Edit `.env.integration_bridge` to match your deployed service URLs.
3. Start the bridge:
```bash
python start_integration_bridge.py
```

### 3. Test Individual Services

Each service has a health endpoint:

```bash
# Prompt Runner
curl http://your-host:8003/health

# Creator Core
curl http://your-host:8000/

# BHIV Core
curl http://your-host:8001/

# Bucket
curl http://your-host:8005/bucket/stats

# Integration Bridge
curl http://your-host:8004/pipeline/health
```

### 4. Test Full Pipeline

Execute the full pipeline through Integration Bridge:

```bash
curl -X POST http://your-bridge-host:8004/pipeline/execute \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Design a residential building for Mumbai"}'
```

## Cloud Deployment Examples

### AWS EC2 / DigitalOcean / GCP

1. **Deploy each service on separate instances:**
   ```
   Instance 1: Prompt Runner (Port 8003)
   Instance 2: Creator Core (Port 8000)
   Instance 3: BHIV Core (Port 8001)
   Instance 4: Bucket (Port 8005)
   Instance 5: Integration Bridge (Port 8004)
   ```

2. **Update environment variables:**
   ```bash
   # On Integration Bridge instance
   export PROMPT_RUNNER_URL=http://instance1-ip:8003
   export CREATOR_CORE_URL=http://instance2-ip:8000
   export BHIV_CORE_URL=http://instance3-ip:8001
   export BUCKET_URL=http://instance4-ip:8005
   ```

3. **Use MongoDB Atlas for database:**
   ```bash
   # On BHIV Core instance
   export USE_MONGODB=true
   export MONGODB_CONNECTION_STRING=mongodb+srv://user:pass@cluster.mongodb.net
   ```

### Docker Deployment

Each service can be containerized:

```dockerfile
# Example for BHIV Core
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8001
CMD ["python", "main.py"]
```

### Kubernetes Deployment

Deploy as separate pods with services:

```yaml
# Example service definition
apiVersion: v1
kind: Service
metadata:
  name: bhiv-core
spec:
  selector:
    app: bhiv-core
  ports:
  - port: 8001
    targetPort: 8001
```

## Production Checklist

- [ ] Set all environment variables
- [ ] Configure MongoDB (if using)
- [ ] Set up SSL/TLS certificates
- [ ] Configure firewall rules
- [ ] Set up logging and monitoring
- [ ] Configure health checks
- [ ] Set up automatic restarts
- [ ] Test service connectivity

## Troubleshooting

### Service Not Reachable
1. Check if service is running: `curl http://host:port/health`
2. Check firewall rules
3. Verify environment variables

### Database Connection Failed
1. Check MongoDB connection string
2. Verify network connectivity
3. Check credentials

### Integration Bridge Errors
1. Check all service URLs are correct
2. Verify all services are healthy
3. Check network connectivity between services
