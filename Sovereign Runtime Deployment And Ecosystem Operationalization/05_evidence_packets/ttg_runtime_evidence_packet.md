# TTG Runtime Evidence Packet

**Product:** Tabletop Game (TTG)  
**Trace ID:** `live_test_d61c664e3559`  
**Classification:** live-service evidence

## Six checklist items

1. **Prompt Runner** — instruction with `product_context: ttg`, tasks include `generate_game_blueprint`
2. **Creator Core** — blueprint envelope generated
3. **Core execution** — full CET → Sarathi → Gate → BHIV chain (A2b–A3 present)
4. **Bucket** — trace retrievable at `/bucket/trace/live_test_d61c664e3559`
5. **InsightFlow** — `instruction.received` events in `bhiv_bucket/insightflow_events.jsonl`
6. **Replay** — `/pipeline/replay/live_test_d61c664e3559` returns 200

## Product output

TTG output adapter applied (`game_content`, `gameplay_structure`, `assets`).
