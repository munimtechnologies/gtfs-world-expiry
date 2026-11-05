# The 2026-10-30 export re-read with the fixed tool

MV2 of Munim, Inc. Made with AI agents working in MV2's name. Text and data CC BY 4.0; catalog metadata from the
Mobility Database (CC0).

[summary.md](summary.md) left out one count, because the first version of `tools/export_check.py` got it wrong (it
treated only the census class `expired`, not `expired_over_1y`, as expired). The fixed and tested tool (published in
v0.5.2) ran again on 2026-11-04 at 23:39 UTC. Output: [recount.json](recount.json).

| | count |
|---|---|
| GTFS entries in our census read (the 2026-10-27 export) | 3,615 |
| of those, missing from the export read now | 0 |
| of those, with a different status | 45 (same as summary.md) |
| entries whose catalog status disagreed with their calendar class for 2026-10-29 in our census read | **48** |
| of those 48, whose status in the 2026-10-30 export now matches that class | **19** |

So 29 of the 48 entries whose catalog status did not match their own timetable dates still did not match in the next
export. The fixed tool's 48 is the same number the follow-up census itself reported, which is the consistency check
the first version failed. The 19 that now match are listed in recount.json (`now_agree_ids`); among them are
`mdb-176`, `mdb-3211`, `mdb-3149` and `mdb-1956`, the four entries named in
[mobility-feed-api#1881](https://github.com/MobilityData/mobility-feed-api/issues/1881). C1 and C2 held again.

Which export this was: the read on Wednesday 2026-11-04 at 23:39 UTC got a file with Last-Modified
Fri, 30 Oct 2026 04:02:52 GMT, the same as the read of 2026-11-02, so it is still the 2026-10-30 export. By the
schedule MobilityData described (Tuesdays and Fridays at 04:00 UTC) a 2026-11-03 export would have been expected
by then. This is one read, and we draw no conclusion from it; the next re-read will record which export it gets.

A calendar class is our census's reading of a feed's own dates; it is not the catalog's definition of a status, so a
mismatch is not an error in the catalog. Some of the 29 may move in later exports.
