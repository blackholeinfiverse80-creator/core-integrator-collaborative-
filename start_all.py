"""
One-Command Startup for BHIV Core-Integrator
Simply run: python start_all.py
"""

import sys
from pathlib import Path
from dotenv import load_dotenv

# Load env variables before starting anything
load_dotenv()

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from core.service_orchestrator import ServiceOrchestrator
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    """Main entry point"""
    try:
        print("\n")
        print("+" + "="*68 + "+")
        print("|" + " "*68 + "|")
        print("|" + " BHIV CORE-INTEGRATOR - ALL SERVICES STARTUP".center(68) + "|")
        print("|" + " "*68 + "|")
        print("+" + "="*68 + "+")
        print()
        
        # Create and run orchestrator
        orchestrator = ServiceOrchestrator()
        
        # Show startup plan
        orchestrator.print_startup_plan()
        
        # Start all services
        if orchestrator.start_services(wait_for_health=True, health_check_timeout=30):
            print("\n[OK] All services started successfully!")
            print("\nService URLs:")
            print("-" * 70)
            
            for service_name in orchestrator.get_startup_order():
                try:
                    from config import ConfigManager
                    url = ConfigManager.get_service_url(service_name)
                    print(f"  {service_name:20s} → {url}")
                except:
                    print(f"  {service_name:20s} → http://127.0.0.1:<port>")
            
            print("-" * 70)
            print("\n🔍 Monitoring services... (Press Ctrl+C to stop)")
            
            # Monitor services continuously
            orchestrator.monitor_services(check_interval=5)
        else:
            print("\n[ERROR] Failed to start all services")
            print("Check the logs above for details")
            sys.exit(1)
    
    except Exception as e:
        print(f"\n[FATAL] Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
