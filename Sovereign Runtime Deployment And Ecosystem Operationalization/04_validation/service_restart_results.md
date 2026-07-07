# Service Restart Results

**Status:** not fully demonstrated  
**Generated:** 2026-07-07

## Observed

Services remained running across the test window. After rate-limit window, TTV and Simulation Runtime pipelines succeeded without manual restart.

## Recommended test

```powershell
# Kill BHIV Core, restart via start_all.py, retry pipeline
python start_all.py
python run_comprehensive_live_tests.py
```

## Pass/fail

- **NOT RUN** — controlled kill-and-restart not executed in this session
- **PARTIAL:** Services recovered from rate-limit window without restart
