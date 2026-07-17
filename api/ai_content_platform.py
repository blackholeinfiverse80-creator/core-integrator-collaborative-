"""
AI Content Platform Integration Router
=======================================
Exposes /pipeline/content endpoint for AI Content Platform consumption.
Routes through BHIVIntegrationBridge full 4-phase pipeline.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from integration_bridge_v2 import BHIVIntegrationBridge

router = APIRouter(prefix="/pipeline", tags=["AI Content Platform"])
_bridge = None


def get_bridge() -> BHIVIntegrationBridge:
    global _bridge
    if _bridge is None:
        _bridge = BHIVIntegrationBridge()
    return _bridge


class ContentRequest(BaseModel):
    prompt: str


@router.post("/content")
async def content_pipeline(request: ContentRequest):
    """Execute full pipeline for AI Content Platform."""
    result = get_bridge().process_full_pipeline(request.prompt)
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result["error"])
    return result


@router.get("/content/health")
async def content_health():
    """Check AI Content Platform pipeline health."""
    return get_bridge().health_check()
