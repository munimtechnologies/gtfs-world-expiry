# feeds_v2.csv re-read against the census read of 2026-10-30 (the 2026-10-27 export)

Read 2026-11-10T05:25:09Z; file Last-Modified Tue, 10 Nov 2026 04:02:52 GMT.

Checks: `{"C1": "held", "C2": "held"}`

| | count |
|---|---|
| GTFS entries in our 2026-10-30 read | 3615 |
| of those, missing from the new file | 1 |
| of those, status changed | 72 |
| status disagreeing with the census's class for 2026-10-29 | 48 |
| of those, status now matches that class | 20 |

Status moves: `{"active->active": 2834, "active->deprecated": 8, "active->future": 3, "active->inactive": 35, "future->active": 4, "future->future": 10, "inactive->active": 17, "inactive->deprecated": 5, "inactive->inactive": 698}`

Named entries now: `{"mdb-176": "inactive", "mdb-3211": "inactive", "mdb-3149": "active", "mdb-1956": "active"}`
