# feeds_v2.csv re-read against the census read of 2026-10-30 (the 2026-10-27 export)

Read 2026-11-06T08:33:04Z; file Last-Modified Fri, 06 Nov 2026 04:02:46 GMT.

Checks: `{"C1": "held", "C2": "held"}`

| | count |
|---|---|
| GTFS entries in our 2026-10-30 read | 3615 |
| of those, missing from the new file | 1 |
| of those, status changed | 76 |
| status disagreeing with the census's class for 2026-10-29 | 48 |
| of those, status now matches that class | 20 |

Status moves: `{"active->active": 2828, "active->deprecated": 8, "active->future": 12, "active->inactive": 32, "future->active": 7, "future->future": 7, "inactive->active": 15, "inactive->deprecated": 2, "inactive->inactive": 703}`

Named entries now: `{"mdb-176": "inactive", "mdb-3211": "inactive", "mdb-3149": "active", "mdb-1956": "active"}`
