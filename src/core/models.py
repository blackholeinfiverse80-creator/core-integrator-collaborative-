from pydantic import BaseModel, Field, root_validator
from typing import Dict, Any, Literal


class CoreRequest(BaseModel):
    """Request model for the core gateway endpoint"""
    module: Literal["finance", "education", "creator", "sample_text", "video"] = Field(..., description="Target module name")
    intent: Literal["generate", "analyze", "review", "get_status", "list_videos", "feedback", "history"] = Field(..., description="Intent for the module to perform")
    user_id: str = Field(..., min_length=1)
    data: Dict[str, Any] = Field(default_factory=dict)


class CoreResponse(BaseModel):
    """Response model for the core gateway endpoint"""
    status: Literal["success", "error"] = Field(..., description="Overall status")
    message: str = Field(..., description="Human-readable message")
    result: Any = Field(default_factory=dict)

    @root_validator(pre=True)
    def ensure_fields(cls, values):
        # Provide safe defaults if modules returned only a raw result
        if 'status' not in values:
            values['status'] = 'success'
        if 'message' not in values:
            values['message'] = ''
        if 'result' not in values and ('word_count' in values or values):
            # If module returned a plain dict (like {'word_count': 3}), put it under result
            values['result'] = values.copy()
        return values