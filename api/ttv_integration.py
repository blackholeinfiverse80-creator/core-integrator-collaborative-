"""
TTV Product Integration Router
==============================
Exposes /pipeline/ttv endpoint for TTV product consumption.
Routes through TANTRAIntegrationBridge — no pipeline bypass allowed.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from src.adapters.tantra_bridge import TANTRAIntegrationBridge

router = APIRouter(prefix="/pipeline", tags=["TTV Integration"])
_bridge = None


def get_bridge() -> TANTRAIntegrationBridge:
    global _bridge
    if _bridge is None:
        _bridge = TANTRAIntegrationBridge()
    return _bridge


class TTVRequest(BaseModel):
    video_type: str
    topic: Optional[str] = ""
    duration: Optional[str] = "5min"
    style: Optional[str] = "standard"
    voice: Optional[str] = "neutral"
    description: Optional[str] = ""


@router.post("/ttv")
async def ttv_pipeline(request: TTVRequest):
    """Execute full pipeline for TTV product."""
    result = get_bridge().process_ttv_request(request.dict())
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result["error"])
    return result


@router.get("/ttv/health")
async def ttv_health():
    """Validate TTV system boundaries and pipeline accessibility."""
    return get_bridge().validate_system_boundaries()
