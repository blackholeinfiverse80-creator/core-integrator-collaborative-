# Gurukul Runtime Evidence Packet

**Product:** Gurukul  
**Trace ID:** `comp_gurukul_8934d450a8` (failed)  
**Classification:** partial — blocked by rate limit

## Status

Pipeline failed with BHIV Core 429 during comprehensive test burst. Adapter code is wired in `integration_bridge.py` (`GurukulInputNormalizer`, `GurukulOutputAdapter`).

## Retry command

```bash
# After restarting services with RATE_LIMIT_IP_PER_MIN=10000
curl -X POST http://127.0.0.1:8004/pipeline/execute \
  -H "X-API-Key: prod_shakti_tantra_secret_key_2026" \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Plan a lesson on algebra for grade 8","product_context":"gurukul"}'
```

## Production proof statement

Wiring exists; live end-to-end proof pending successful execution without rate-limit collision.
