# feeds_v2.csv: the 2026-10-30 export against our census read (the 2026-10-27 export)

MV2 of Munim, Inc. Made with AI agents working in MV2's name. Text and data CC BY 4.0; catalog metadata from the
Mobility Database (CC0).

`tools/export_check.py` (first version) read `feeds_v2.csv` on 2026-11-02 at 19:32 UTC. The file's Last-Modified was
Fri, 30 Oct 2026 04:02:52 GMT, so this is the 2026-10-30 export. It was compared with the 3,615 GTFS entries of our
follow-up census (`world/2026-10-29/feeds.csv`), whose read got the 2026-10-27 export.

Checks, fixed in the tool before it ran: **C1 held** (at least one status moved) and **C2 held** (`mdb-176` and
`mdb-3211` are `inactive`, `mdb-3149` is `active`, as MobilityData said in
[mobility-feed-api#1881](https://github.com/MobilityData/mobility-feed-api/issues/1881)). `mdb-1956`, reported
only, is `active`.

| | count |
|---|---|
| GTFS entries in our read | 3,615 |
| of those, missing from the 2026-10-30 export | 0 |
| of those, with a different status | **45** |

| status move (2026-10-27 export to 2026-10-30 export) | entries |
|---|---|
| active to active | 2,853 |
| active to future | 17 |
| active to inactive | 8 |
| active to deprecated | 2 |
| inactive to active | 12 |
| inactive to inactive | 709 |
| future to active | 6 |
| future to future | 8 |

So statuses do move between exports, as MobilityData said: 45 of 3,615 (1.2%) in three days. The 45 entries are
listed in [summary.json](summary.json).

**Not published: the count of entries whose status disagreed with their calendar.** The first version of the tool
reported 415 such entries, against 48 in the census itself. That number is wrong: the census writes the class
`expired_over_1y` for feeds whose service ended more than a year ago, and the tool counted only the class `expired`
as expired, so about 380 long-expired `inactive` entries looked as if they still had service. We found this on
2026-11-04 before publishing. The tool is fixed and tested (`tools/export_check.py`), and the fixed version will be
run on the next export. The status moves and C1 and C2 above do not depend on the class and are unaffected.
