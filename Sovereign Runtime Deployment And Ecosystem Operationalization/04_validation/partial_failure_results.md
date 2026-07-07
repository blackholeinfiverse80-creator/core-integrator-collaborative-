# Partial Failure Results

- Observed partial failure before routing fix: trace `f55e5b1116974a6eaf77ed9ba9b5c30e` rejected at Sarathi with `invalid_contract: has_valid_module`.
- Root cause: bridge passed malformed routing decision to CET; contract had missing `target_module`.
- Fix: derive explicit routing decision (`module_path`, `execution_intent`, `execution_data`) before CET call.
- Post-fix success trace: `bca7148540f14b63a501e21e99e49253`.
