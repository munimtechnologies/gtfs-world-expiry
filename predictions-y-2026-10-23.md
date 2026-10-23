# Predictions recorded before the status-lag follow-up (2026-10-23)

Written on 2026-10-23 (about 23:00 UTC), after the second census (`world/2026-10-22-all/`) and before the census it
will be compared with. The follow-up census will be run on or after 2026-10-30 with the same tool and settings
(`tools/world_expiry.py --statuses active,inactive,future`). `tools/world_diff.py --predictions Y` compares the two
files and scores Y1 to Y6, which are also fixed in `PREDICTIONS_Y` in that tool. Every result will be reported,
including the misses.

**The question.** The Mobility Database sets a feed's status from the service date range of its latest dataset
([feed_status.py](https://github.com/MobilityData/mobility-feed-api/blob/main/functions-python/helpers/feed_status.py)).
In the second census, 38 entries disagreed with their own calendars: 24 active entries with no service left, and 14
inactive entries that still had service left. How many of these disagreements fix themselves within a week, and how
many stay?

**What was already known when these were written** (hand checks on mobilitydatabase.org, 2026-10-23):
- Of the 24 active entries with no service left, 7 were checked. 6 show no service date range for their latest
  dataset: `mdb-2234`, `tld-5769`, `mdb-912`, `mdb-3470`, `tdg-83969`, `tdg-84018`. The status job skips datasets
  without a range, so we expect these to stay `active`. The 7th, `mdb-176`, is a seasonal feed with a range ending
  2026-10-20 (2026-10-21 in its history table). `mdb-3211` serves the same file.
- Of the 14 inactive entries with service left, 3 were checked. Each got a new dataset shortly before the catalog file
  was read: `mdb-3149` (downloaded 2026-10-20), `mdb-1956` (2026-10-20; a feed that is replaced every week),
  `tdg-82148` (2026-10-23). Their pages show an "Active" label beside the new range, but `feeds_v2.csv` still listed
  them as `inactive`.

**Groups**, taken from `world/2026-10-22-all/feeds.csv` (feeds whose calendar was read):
- `inactive_running`: status inactive, service left on the as-of date (14 entries).
- `active_stuck`: status active, no service left for 30 days or more (19 entries).
- `active_recent`: status active, no service left for less than 30 days (5 entries).

A status *agrees* with the calendar when an inactive feed has no service left, or an active or future feed has some.
Shares are of the group's entries that are in the follow-up census and read there. Entries that left the file
(deprecated, development or removed) are reported separately and are not counted as agreeing.

| | Prediction | Basis |
|---|---|---|
| Y1 | Of the `inactive_running` entries, at least 60% agree in the follow-up census. | The three checked ones look like a status that had not caught up with a new dataset. A weekly feed can fall behind again, so not all will agree. |
| Y2 | Of the `active_stuck` entries, at least 80% still disagree. | 6 of 7 checked entries have no service date range, so the status job never touches them. |
| Y3 | All six entries listed above with no service date range that are read in the follow-up census still disagree. | Same mechanism, entry by entry. |
| Y4 | Both `mdb-176` and `mdb-3211`, if read, agree in the follow-up census. | Their range has ended, so the status job should set them inactive, unless a new season's file arrives first, which would also agree. |
| Y5 | In the follow-up census, between 15 and 40 active entries have no service left. | The stuck entries persist and new seasonal ends add a few. |
| Y6 | In the follow-up census, between 3 and 40 inactive entries still have service left. | If the lag comes from new datasets arriving before the status is refreshed, it recurs every week with different feeds. |

Limits stated in advance: both censuses read the catalog's mirror, not the publisher's URL. We do not know when
`feeds_v2.csv` is exported or how often the status job runs, so a disagreement may be a matter of hours or of
months. These predictions only test what one week later looks like. Seven hand checks of 24, and three of 14, are
small samples.

MV2 of Munim, Inc. Made with AI agents working in MV2's name. Text CC BY 4.0.
