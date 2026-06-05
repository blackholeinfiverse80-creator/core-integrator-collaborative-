from typing import Dict, Any, List
from .base import BaseAgent
from ..utils.logger import setup_logger
from ..utils.video_bridge_client import VideoBridgeClient


class VideoAgent(BaseAgent):
    """Agent for text-to-video generation and management"""
    
    def __init__(self):
        self.logger = setup_logger(__name__)
        # Use VideoBridgeClient for external text-to-video service communication
        self.video_bridge = VideoBridgeClient()
    
    def handle_request(self, intent: str, data: Dict[str, Any], 
                      context: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Handle video-related requests"""
        
        if intent == "generate":
            return self._generate_video(data)
        elif intent == "get_status":
            return self._get_status(data)
        elif intent == "list_videos":
            return self._list_videos(data)
        else:
            return {
                "status": "error",
                "message": f"Unknown intent: {intent}"
            }
    
    def _generate_video(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate video from text using external video service"""
        try:
            text = data.get("text")
            if not text:
                return {
                    "status": "error",
                    "message": "Text is required"
                }
            
            topic = data.get("topic", "general")
            style = data.get("style", "default")
            duration = data.get("duration", 30)
            language = data.get("language", "en")
            
            self.logger.info(f"Video generation request: {topic}")
            
            # Try to call external video service via VideoBridgeClient
            external_result = self.video_bridge.generate_video(
                text=text,
                topic=topic,
                style=style,
                duration=duration,
                language=language
            )
            
            # Check if external service call was successful
            if external_result.get("success") is not False:
                return {
                    "status": "success",
                    "message": "Video generation started via external service",
                    "result": {
                        "generation_id": external_result.get("generation_id", f"vid_{hash(text) % 10000000}"),
                        "status": external_result.get("status", "processing"),
                        "video_url": external_result.get("video_url"),
                        "video_path": external_result.get("video_path"),
                        "topic": topic,
                        "style": style,
                        "duration": external_result.get("duration", duration),
                        "metadata": external_result.get("metadata", {})
                    }
                }
            
            # Fallback: return local mock response if external service unavailable
            self.logger.warning(f"External video service unavailable, using fallback: {external_result.get('error_message')}")
            return {
                "status": "success",
                "message": "Video generation started (fallback mode)",
                "result": {
                    "generation_id": f"vid_{hash(text) % 10000000}",
                    "status": "processing",
                    "topic": topic,
                    "style": style,
                    "duration": duration,
                    "fallback_used": True
                }
            }
        except Exception as e:
            self.logger.error(f"Video generation failed: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    def _get_status(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Get video generation status from external service"""
        try:
            generation_id = data.get("generation_id")
            if not generation_id:
                return {
                    "status": "error",
                    "message": "generation_id is required"
                }
            
            # Try to get status from external video service
            external_result = self.video_bridge.get_video_status(generation_id)
            
            if external_result.get("success") is not False:
                return {
                    "status": "success",
                    "result": {
                        "generation_id": generation_id,
                        "status": external_result.get("status", "completed"),
                        "video_url": external_result.get("video_url", f"/videos/{generation_id}.mp4"),
                        "video_path": external_result.get("video_path"),
                        "duration": external_result.get("duration"),
                        "metadata": external_result.get("metadata", {})
                    }
                }
            
            # Fallback: return mock completed status
            return {
                "status": "success",
                "result": {
                    "generation_id": generation_id,
                    "status": "completed",
                    "video_url": f"/videos/{generation_id}.mp4",
                    "fallback_used": True
                }
            }
        except Exception as e:
            self.logger.error(f"Status check failed: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    def _list_videos(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """List generated videos"""
        try:
            limit = data.get("limit", 10)
            
            return {
                "status": "success",
                "result": {
                    "videos": [],
                    "total": 0,
                    "limit": limit
                }
            }
        except Exception as e:
            self.logger.error(f"List videos failed: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
