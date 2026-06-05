#!/usr/bin/env python3
"""
Security Hardening Middleware - Risk Reduction Only
WARNING: This does NOT make the system secure - only reduces exploitability
"""

import re
import time
import hashlib
from collections import defaultdict, deque
from typing import Dict, Any, Optional
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import logging

# Security logger
security_logger = logging.getLogger("security")
security_logger.setLevel(logging.WARNING)

class SecurityHardening:
    def __init__(self):
        # Rate limiting storage
        self.ip_requests = defaultdict(lambda: deque(maxlen=100))
        self.user_requests = defaultdict(lambda: deque(maxlen=50))
        
        # Suspicious pattern detection
        self.cross_user_access = defaultdict(set)
        self.enumeration_attempts = defaultdict(int)
        
        # User ID validation pattern
        self.valid_user_id_pattern = re.compile(r'^[a-zA-Z0-9_-]{1,64}$')
        
    def validate_user_id(self, user_id: str) -> bool:
        """Strict user_id validation"""
        if not user_id or not isinstance(user_id, str):
            return False
        if len(user_id) > 64 or len(user_id) < 1:
            return False
        if not self.valid_user_id_pattern.match(user_id):
            return False
        return True
        
    def check_rate_limits(self, request: Request, user_id: Optional[str] = None) -> bool:
        """Rate limiting per IP and user"""
        client_ip = request.client.host
        now = time.time()
        
        # IP-based rate limiting (60 requests per minute)
        ip_times = self.ip_requests[client_ip]
        ip_times.append(now)
        recent_ip_requests = sum(1 for t in ip_times if now - t < 60)
        
        if recent_ip_requests > 60:
            security_logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            return False
            
        # User-based rate limiting (30 requests per minute)
        if user_id:
            user_times = self.user_requests[user_id]
            user_times.append(now)
            recent_user_requests = sum(1 for t in user_times if now - t < 60)
            
            if recent_user_requests > 30:
                security_logger.warning(f"Rate limit exceeded for user: {user_id[:8]}...")
                return False
                
        return True
        
    def detect_enumeration(self, request: Request, user_id: str) -> bool:
        """Detect user enumeration patterns"""
        client_ip = request.client.host
        
        # Track unique user_ids per IP
        self.cross_user_access[client_ip].add(user_id)
        
        # Alert if IP accesses too many different users
        if len(self.cross_user_access[client_ip]) > 10:
            security_logger.warning(f"Potential enumeration from IP: {client_ip}")
            self.enumeration_attempts[client_ip] += 1
            
            # Block after repeated enumeration attempts
            if self.enumeration_attempts[client_ip] > 3:
                return False
                
        return True
        
    def sanitize_response(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Remove internal details from responses"""
        if not isinstance(response_data, dict):
            return response_data
            
        sanitized = {}
        
        # Safe fields to include
        safe_fields = {
            'status', 'message', 'result', 'timestamp', 
            'integration_ready', 'integration_score'
        }
        
        for key, value in response_data.items():
            if key in safe_fields:
                if isinstance(value, dict):
                    sanitized[key] = self.sanitize_nested_dict(value)
                elif isinstance(value, list):
                    sanitized[key] = [self.sanitize_nested_dict(item) if isinstance(item, dict) else item for item in value]
                else:
                    sanitized[key] = value
                    
        return sanitized
        
    def sanitize_nested_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize nested dictionaries"""
        # Remove dangerous fields
        dangerous_fields = {
            'db_path', 'adapter_type', 'modules', 'module_load_status',
            'components', 'memory', 'security', 'failing_components',
            'readiness_reason', 'signature', 'details', 'insightflow_event'
        }
        
        return {k: v for k, v in data.items() if k not in dangerous_fields}

# Global security instance
security = SecurityHardening()

async def security_middleware(request: Request, call_next):
    """Security middleware for all requests"""
    try:
        # Apply security checks
        if not security.check_rate_limits(request):
            return JSONResponse(
                status_code=429,
                content={"error": "Rate limit exceeded"}
            )
            
        response = await call_next(request)
        return response
        
    except Exception as e:
        # Generic error response - no internal details
        security_logger.error(f"Security middleware error: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error"}
        )

def validate_user_request(user_id: str, request: Request) -> str:
    """Validate user_id and detect suspicious patterns"""
    # Strict user_id validation
    if not security.validate_user_id(user_id):
        raise HTTPException(status_code=400, detail="Invalid user identifier format")
        
    # Enumeration detection
    if not security.detect_enumeration(request, user_id):
        raise HTTPException(status_code=429, detail="Access pattern blocked")
        
    # Additional rate limiting for this user
    if not security.check_rate_limits(request, user_id):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
        
    return user_id