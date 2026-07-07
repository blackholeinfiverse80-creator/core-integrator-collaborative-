"""
BHIV Integration Bridge - Full Pipeline Orchestrator
====================================================
Connects: Prompt Runner → Creator Core → BHIV Core → Bucket

Enforces strict trace_id and workflow_id propagation across all endpoints,
secured with API key middleware.
"""

import json
import os
import uuid
import requests
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class ArtifactGraph:
    """Manages the artifact chain: A1 → A2 → A3 → A4"""
    
    def __init__(self, bucket_url: str = "http://127.0.0.1:8005"):
        self.artifacts = {}
        self.bucket_url = bucket_url
        
    def create_chain(self, trace_id: str, workflow_id: str, instruction: Dict[str, Any], headers: Dict[str, str]) -> Dict[str, str]:
        """Create full artifact chain for a request"""
        chain = {
            "trace_id": trace_id,
            "workflow_id": workflow_id,
            "A1_instruction": self._store_artifact("instruction", instruction, trace_id, workflow_id, headers),
            "A2_blueprint": None,  # Set after Creator Core
            "A3_execution": None,  # Set after Core execution
            "A4_result": None      # Set after final result
        }
        self.artifacts[trace_id] = chain
        return chain
        
    def update_artifact(self, trace_id: str, workflow_id: str, artifact_type: str, data: Dict[str, Any], headers: Dict[str, str]) -> str:
        """Update artifact in chain"""
        artifact_id = self._store_artifact(artifact_type, data, trace_id, workflow_id, headers)
        if trace_id in self.artifacts:
            self.artifacts[trace_id][f"A{self._get_artifact_number(artifact_type)}_{artifact_type}"] = artifact_id
        return artifact_id
        
    def _store_artifact(self, artifact_type: str, data: Dict[str, Any], trace_id: str, workflow_id: str, headers: Dict[str, str]) -> str:
        """Store individual artifact to bucket"""
        artifact_id = f"{artifact_type}_{uuid.uuid4().hex[:8]}"
        
        # Inject workflow_id into data for storage correlation
        data_to_store = data.copy() if isinstance(data, dict) else {"raw": data}
        data_to_store["workflow_id"] = workflow_id
        data_to_store["trace_id"] = trace_id
        
        try:
            # Store to BHIV Bucket
            response = requests.post(
                f"{self.bucket_url}/bucket/store",
                json={
                    "artifact_id": artifact_id,
                    "artifact_type": artifact_type,
                    "data": data_to_store,
                    "trace_id": trace_id
                },
                headers=headers,
                timeout=10
            )
            if response.status_code != 200:
                print(f"Warning: Failed to store artifact {artifact_id} to bucket: {response.text}")
        except Exception as e:
            print(f"Warning: Bucket storage failed for {artifact_id}: {str(e)}")
            
        return artifact_id
        
    def _get_artifact_number(self, artifact_type: str) -> int:
        mapping = {"instruction": 1, "blueprint": 2, "execution": 3, "result": 4}
        return mapping.get(artifact_type, 0)


class BHIVIntegrationBridge:
    """Main integration orchestrator"""
    
    def __init__(self):
        self.prompt_runner_url = os.getenv("PROMPT_RUNNER_URL", "http://127.0.0.1:8003")
        self.creator_core_url = os.getenv("CREATOR_CORE_URL", "http://127.0.0.1:8000")
        self.bhiv_core_url = os.getenv("BHIV_CORE_URL", "http://127.0.0.1:8001")
        self.bucket_url = os.getenv("BUCKET_URL", "http://127.0.0.1:8005")
        self.artifact_graph = ArtifactGraph(self.bucket_url)
        
    def process_full_pipeline(self, user_prompt: str, trace_id: Optional[str] = None, workflow_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute complete pipeline: Prompt → Instruction → Blueprint → Execution → Result
        
        Returns full trace with artifact chain
        """
        trace_id = trace_id or f"trace_{uuid.uuid4().hex[:12]}"
        workflow_id = workflow_id or f"wf_{uuid.uuid4().hex[:12]}"
        
        # Build authentication headers
        api_key = os.getenv("AUTH_API_KEY", "")
        headers = {
            "X-Trace-Id": trace_id,
            "X-Workflow-Id": workflow_id
        }
        if api_key:
            headers["X-API-Key"] = api_key
            
        try:
            # PHASE 1: Prompt Runner → Structured Instruction
            instruction = self._call_prompt_runner(user_prompt, headers)
            instruction["trace_id"] = trace_id
            instruction["workflow_id"] = workflow_id
            instruction["instruction_id"] = trace_id
            
            # Create artifact chain
            chain = self.artifact_graph.create_chain(trace_id, workflow_id, instruction, headers)
            
            # PHASE 2: Creator Core → Blueprint Generation  
            blueprint = self._call_creator_core(instruction, headers)
            blueprint["trace_id"] = trace_id
            blueprint["workflow_id"] = workflow_id
            self.artifact_graph.update_artifact(trace_id, workflow_id, "blueprint", blueprint, headers)
            
            # PHASE 3: BHIV Core → Execution
            execution_result = self._call_bhiv_core(blueprint, trace_id, workflow_id, headers)
            execution_result["trace_id"] = trace_id
            execution_result["workflow_id"] = workflow_id
            self.artifact_graph.update_artifact(trace_id, workflow_id, "execution", execution_result, headers)
            
            # PHASE 4: Final Result Assembly
            final_result = self._assemble_final_result(instruction, blueprint, execution_result)
            final_result["trace_id"] = trace_id
            final_result["workflow_id"] = workflow_id
            self.artifact_graph.update_artifact(trace_id, workflow_id, "result", final_result, headers)
            
            return {
                "status": "success",
                "trace_id": trace_id,
                "workflow_id": workflow_id,
                "artifact_chain": self.artifact_graph.artifacts[trace_id],
                "pipeline_result": final_result,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            return {
                "status": "error", 
                "trace_id": trace_id,
                "workflow_id": workflow_id,
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    def _call_prompt_runner(self, prompt: str, headers: Dict[str, str]) -> Dict[str, Any]:
        """Phase 1: Convert prompt to structured instruction"""
        response = requests.post(
            f"{self.prompt_runner_url}/generate",
            json={"prompt": prompt},
            headers=headers,
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    
    def _call_creator_core(self, instruction: Dict[str, Any], headers: Dict[str, str]) -> Dict[str, Any]:
        """Phase 2: Generate blueprint from instruction"""
        # Filter out extra keys that are forbidden by creator-core PromptRunnerInstruction model
        allowed_keys = {"prompt", "module", "intent", "topic", "tasks", "output_format", "product_context"}
        clean_instruction = {k: v for k, v in instruction.items() if k in allowed_keys}
        
        response = requests.post(
            f"{self.creator_core_url}/creator-core/generate-blueprint", 
            json=clean_instruction,
            headers=headers,
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    
    def _call_bhiv_core(self, blueprint: Dict[str, Any], trace_id: str, workflow_id: str, headers: Dict[str, str]) -> Dict[str, Any]:
        """Phase 3: Execute blueprint through BHIV Core"""
        blueprint_data = blueprint.get("blueprint", blueprint)
        
        # Convert to Core request format
        core_request = {
            "module": "creator",
            "intent": "generate", 
            "user_id": f"bhiv_user_{uuid.uuid4().hex[:8]}",
            "data": {
                "blueprint": blueprint_data.get("payload", blueprint_data),
                "target_product": blueprint_data.get("target_product", "creator"),
                "trace_id": trace_id,
                "workflow_id": workflow_id
            }
        }
        
        response = requests.post(
            f"{self.bhiv_core_url}/core",
            json=core_request,
            headers=headers,
            timeout=45
        )
        response.raise_for_status()
        return response.json()
    
    def _assemble_final_result(self, instruction: Dict[str, Any], blueprint: Dict[str, Any], 
                               execution: Dict[str, Any]) -> Dict[str, Any]:
        """Phase 4: Assemble final result"""
        return {
            "original_prompt": instruction.get("prompt"),
            "generated_instruction": instruction,
            "blueprint_envelope": blueprint,
            "execution_result": execution,
            "pipeline_status": "completed",
            "deterministic_hash": self._compute_hash(instruction, blueprint, execution)
        }
    
    def _compute_hash(self, *args) -> str:
        """Compute deterministic hash for replay validation"""
        combined = json.dumps(args, sort_keys=True)
        import hashlib
        return hashlib.sha256(combined.encode()).hexdigest()[:16]
    
    def replay_from_trace(self, trace_id: str, headers: Dict[str, str]) -> Dict[str, Any]:
        """Replay pipeline from stored trace"""
        try:
            response = requests.get(f"{self.bucket_url}/bucket/trace/{trace_id}", headers=headers, timeout=10)
            if response.status_code == 200:
                bucket_data = response.json()
                return {
                    "status": "success",
                    "trace_id": trace_id,
                    "artifact_chain": bucket_data.get("artifacts", []),
                    "replay_timestamp": datetime.now(timezone.utc).isoformat(),
                    "source": "bucket"
                }
        except Exception as e:
            print(f"Bucket replay failed: {str(e)}")
            
        if trace_id not in self.artifact_graph.artifacts:
            return {"status": "error", "message": "Trace not found"}
            
        chain = self.artifact_graph.artifacts[trace_id]
        return {
            "status": "success",
            "trace_id": trace_id,
            "artifact_chain": chain,
            "replay_timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "local"
        }
    
    def health_check(self, headers: Dict[str, str]) -> Dict[str, Any]:
        """Check all pipeline components"""
        components = {
            "prompt_runner": self._check_component(f"{self.prompt_runner_url}/health", headers),
            "creator_core": self._check_component(f"{self.creator_core_url}/", headers),
            "bhiv_core": self._check_component(f"{self.bhiv_core_url}/", headers),
            "bucket": self._check_component(f"{self.bucket_url}/bucket/stats", headers)
        }
        
        all_healthy = all(comp["status"] == "healthy" for comp in components.values())
        
        return {
            "pipeline_status": "healthy" if all_healthy else "degraded",
            "components": components,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    def _check_component(self, url: str, headers: Dict[str, str]) -> Dict[str, Any]:
        """Check individual component health"""
        try:
            response = requests.get(url, headers=headers, timeout=5)
            return {"status": "healthy", "code": response.status_code}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}


# Integration API endpoints
from fastapi import FastAPI, HTTPException, Request, Depends
from pydantic import BaseModel
from src.utils.security_hardening import security_middleware
from src.utils.auth import auth_middleware, require_auth
from src.utils.observability import observability_middleware

app = FastAPI(
    title="BHIV Integration Bridge",
    description="Full pipeline orchestrator: Prompt Runner → Creator Core → BHIV Core → Bucket",
    version="1.0.0"
)

# Apply global security, auth, and observability middleware
# Middleware order: execution order: observability → auth → security
app.middleware("http")(security_middleware)
app.middleware("http")(auth_middleware)
app.middleware("http")(observability_middleware)

bridge = BHIVIntegrationBridge()

class PipelineRequest(BaseModel):
    prompt: str
    trace_id: Optional[str] = None
    workflow_id: Optional[str] = None

@app.post("/pipeline/execute", dependencies=[Depends(require_auth)])
async def execute_pipeline(request: PipelineRequest, http_req: Request):
    """Execute full BHIV pipeline"""
    # Extract IDs from headers or request state if available
    trace_id = request.trace_id or http_req.state.trace_id
    workflow_id = request.workflow_id or http_req.state.workflow_id
    
    result = bridge.process_full_pipeline(request.prompt, trace_id, workflow_id)
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result["error"])
    return result

@app.get("/pipeline/health")
async def pipeline_health(http_req: Request):
    """Check pipeline component health"""
    api_key = os.getenv("AUTH_API_KEY", "")
    headers = {"X-API-Key": api_key} if api_key else {}
    return bridge.health_check(headers)

@app.get("/health")
async def health(http_req: Request):
    """Alias for pipeline health check used by orchestrator"""
    return await pipeline_health(http_req)

@app.get("/pipeline/replay/{trace_id}", dependencies=[Depends(require_auth)])
async def replay_pipeline(trace_id: str):
    """Replay pipeline from trace ID"""
    api_key = os.getenv("AUTH_API_KEY", "")
    headers = {"X-API-Key": api_key} if api_key else {}
    result = bridge.replay_from_trace(trace_id, headers)
    if result["status"] == "error":
        raise HTTPException(status_code=404, detail=result["message"])
    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)