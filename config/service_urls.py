"""
Service URL Configuration for Independent Deployment
=====================================================
Each service can be deployed separately and configured via environment variables.
"""

import os
from typing import Dict

# Service URL Configuration
# Each service reads these from environment variables

SERVICE_URLS = {
    "prompt_runner": os.getenv("PROMPT_RUNNER_URL", "https://prompt-runner.onrender.com"),
    "creator_core": os.getenv("CREATOR_CORE_URL", "http://127.0.0.1:8000"),
    "bhiv_core": os.getenv("BHIV_CORE_URL", "http://127.0.0.1:8001"),
    "integration_bridge": os.getenv("INTEGRATION_BRIDGE_URL", "http://127.0.0.1:8004"),
    "bucket": os.getenv("BUCKET_URL", "http://127.0.0.1:8005"),
}


def get_service_url(service_name: str) -> str:
    """Get URL for a specific service"""
    return SERVICE_URLS.get(service_name, f"http://127.0.0.1:8000")


def get_all_service_urls() -> Dict[str, str]:
    """Get all service URLs"""
    return SERVICE_URLS.copy()


def print_service_urls():
    """Print all configured service URLs"""
    print("\n" + "="*70)
    print("SERVICE URLS CONFIGURATION")
    print("="*70)
    for name, url in SERVICE_URLS.items():
        env_var = f"{name.upper()}_URL"
        print(f"  {name:20s} -> {url}")
        print(f"  {'(set via ' + env_var + ')':20s}")
    print("="*70 + "\n")


# Environment template for deployment
DEPLOYMENT_ENV_TEMPLATE = """
# BHIV Services URL Configuration
# Copy this to your .env file and update URLs for your deployment

# Prompt Runner Service
PROMPT_RUNNER_URL=http://your-prompt-runner-host:8003

# Creator Core Service
CREATOR_CORE_URL=http://your-creator-core-host:8000

# BHIV Core Service
BHIV_CORE_URL=http://your-bhiv-core-host:8001

# Integration Bridge Service
INTEGRATION_BRIDGE_URL=http://your-bridge-host:8004

# Bucket Service
BUCKET_URL=http://your-bucket-host:8005

# Database Configuration (for BHIV Core)
USE_MONGODB=false
MONGODB_CONNECTION_STRING=mongodb://localhost:27017
MONGODB_DATABASE_NAME=bhiv_production

# Optional: Noopur Integration
INTEGRATOR_USE_NOOPUR=false
NOOPUR_BASE_URL=http://localhost:5001
"""


if __name__ == "__main__":
    print_service_urls()
    print("\nFor deployment, set these environment variables:")
    print(DEPLOYMENT_ENV_TEMPLATE)
