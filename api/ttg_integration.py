"""
TTG Product Integration Router
==============================
Exposes /pipeline/ttg endpoint for TTG product consumption.
Routes through TANTRAIntegrationBridge — no pipeline bypass allowed.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from src.adapters.tantra_bridge import TANTRAIntegrationBridge

router = APIRouter(prefix="/pipeline", tags=["TTG Integration"])
_bridge = None


def get_bridge() -> TANTRAIntegrationBridge:
    global _bridge
    if _bridge is None:
        _bridge = TANTRAIntegrationBridge()
    return _bridge


class TTGRequest(BaseModel):
    game_type: str
    theme: Optional[str] = ""
    difficulty: Optional[str] = "medium"
    player_count: Optional[int] = 1
    description: Optional[str] = ""


@router.post("/ttg")
async def ttg_pipeline(request: TTGRequest):
    """Execute full pipeline for TTG product."""
    result = get_bridge().process_ttg_request(request.dict())
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result["error"])
    return result


@router.get("/ttg/health")
async def ttg_health():
    """Validate TTG system boundaries and pipeline accessibility."""
    return get_bridge().validate_system_boundaries()
