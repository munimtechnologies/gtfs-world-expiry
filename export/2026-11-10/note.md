# feeds_v2.csv re-read on 2026-11-10: the Tuesday export arrived (2026-11-10 04:02 UTC)

MV2 of Munim, Inc. (mv2@munimtech.com). Made with AI agents working in MV2's name. Text CC BY 4.0.

`tools/export_check.py` (commit 454e292, v0.5.2, tests passed) read MobilityData's `feeds_v2.csv` on 2026-11-10 at
05:25:09 UTC. The file's `Last-Modified` header was **Tue, 10 Nov 2026 04:02:52 GMT**, the Tuesday export, about 80
minutes after it was written. On 2026-11-05 we had still received the Friday 2026-10-30 file instead of the Tuesday
2026-11-03 one ([../2026-11-06/note.md](../2026-11-06/note.md)); this time the read matched the published schedule
(Tuesdays and Fridays, 04:00 UTC).

Against our census read (the 2026-10-27 export, 3,615 GTFS entries):

| | 2026-11-06 export | 2026-11-10 export |
|---|---|---|
| entries missing from the new file | 1 | 1 |
| entries whose status changed since our read | 76 | 72 |
| entries whose status disagreed with their own calendar on 2026-10-29 | 48 | 48 |
| of those, status now matches the calendar's class | 20 | 20 |

Status moves since our read (2026-11-10 export): 35 active to inactive, 17 inactive to active, 3 active to future,
4 future to active, 8 active to deprecated, 5 inactive to deprecated. Fewer entries show a change than on 2026-11-06
because some are back at the status of our read: 12 entries showed active to future on 2026-11-06, and 3 do now. The four
entries our #1881 report named read `mdb-176` inactive, `mdb-3211` inactive, `mdb-3149` active and `mdb-1956`
active, as in the two previous exports. Checks C1 and C2 held.

The 72 changed entries include three Japanese entries that MV2's
[gtfs-jp-lapses](https://github.com/munimtechnologies/gtfs-jp-lapses) follows: `jbda-kamishihorotown-kamishihoro`,
`jbda-kamishihorotown-kamishihoro-self-bus` and `jbda-rokkashovillage-rokkasho-sharedtaxi`. The weekly watch of the
GTFS Data Repository will check those feeds at the source.

The 28 entries that still disagree with their calendar class of 2026-10-29 were not re-examined. Their calendars
were read on 2026-10-30, so some of them may have changed since. Datasets with no service date range, one known cause
of disagreement, are tracked by MobilityData in
[mobility-feed-api#1209](https://github.com/MobilityData/mobility-feed-api/issues/1209).

Raw output: [summary.json](summary.json), [summary.md](summary.md).
