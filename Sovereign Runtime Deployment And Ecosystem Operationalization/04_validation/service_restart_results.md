# Service Restart Results

- Action: force-killed BHIV Core listener process on port 8001, then relaunched using `python start_all.py`.
- Outcome: service recovered to healthy state and subsequent live pipeline requests succeeded.
- Evidence traces after restart: `41ea7d8193c14d308b45e2fe90a5acc0`, `b42bc62531bb405b808be4e1fd5f505e`, `e8312062eef44470a7f764937887ef47`.
