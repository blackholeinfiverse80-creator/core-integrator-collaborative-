# Replay After Recovery Results

- Command: GET `/pipeline/replay/<trace_id>` using API key after BHIV restart.
- Verified traces: `5363db20b91848a8b9e920e1dfd3d82c`, `41ea7d8193c14d308b45e2fe90a5acc0`, `b42bc62531bb405b808be4e1fd5f505e`, `e8312062eef44470a7f764937887ef47`.
- Outcome: all replay calls returned HTTP 200 and artifact chains from bucket.
