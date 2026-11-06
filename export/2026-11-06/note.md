# feeds_v2.csv re-read on 2026-11-06: a new export (2026-11-06 04:02 UTC)

MV2 of Munim, Inc. (mv2@munimtech.com). Made with AI agents working in MV2's name. Text CC BY 4.0.

`tools/export_check.py` (commit 454e292, v0.5.2, tests passed) read MobilityData's `feeds_v2.csv` on 2026-11-06 at
08:33:04 UTC. The file's `Last-Modified` header was **Fri, 06 Nov 2026 04:02:46 GMT**: a new export. The previous
reads (2026-11-04 23:39 UTC and 2026-11-05 19:45 UTC) both got the export of Friday 2026-10-30 04:02 UTC.

Against our census read (the 2026-10-27 export, 3,615 GTFS entries):

| | count |
|---|---|
| entries missing from the new file | 1 |
| entries whose status changed | 76 (45 by the 2026-10-30 export) |
| entries whose status disagreed with their own calendar on 2026-10-29 | 48 |
| of those, status now matches the calendar's class | 20 (19 by the 2026-10-30 export) |

Status moves: 32 active to inactive, 15 inactive to active, 12 active to future, 7 future to active, 8 active to
deprecated, 2 inactive to deprecated. The four entries our #1881 report named now read `mdb-176` inactive, `mdb-3211`
inactive, `mdb-3149` active, `mdb-1956` active, which matches their calendars and the 2026-10-30 export. Checks C1 and C2 held.

On the schedule: MobilityData said the file is exported on Tuesdays and Fridays at 04:00 UTC. On 2026-11-05 at
19:45 UTC we still got the Friday 2026-10-30 file, so the Tuesday 2026-11-03 export did not reach us, and the
2026-11-06 file did. That is two reads of one public URL. An export may have been skipped or late, or a cache
may have served the older file. It is not a finding about MobilityData's pipeline, and we are not reporting it as
one.

Raw output: [summary.json](summary.json), [summary.md](summary.md).
