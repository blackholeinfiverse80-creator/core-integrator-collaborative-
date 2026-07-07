# TTG Onboarding

- Trace ID: `5363db20b91848a8b9e920e1dfd3d82c`
- Prompt Runner participation: confirmed via `/pipeline/execute` with `product_context=ttg`.
- Creator Core participation: blueprint stored in bucket trace chain.
- Core execution participation: CET -> Sarathi -> Gate -> BHIV execution all present (A2b..A3).
- Bucket persistence: replay output includes stored artifacts for trace.
- InsightFlow telemetry: integration bridge emits lineage event to `bhiv_bucket/insightflow_events.jsonl`.
- Replay capability: verified via `/pipeline/replay/5363db20b91848a8b9e920e1dfd3d82c` (status 200).
