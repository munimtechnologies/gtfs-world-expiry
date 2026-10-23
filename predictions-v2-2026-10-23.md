# Predictions recorded before the second census (2026-10-23)

Written on 2026-10-23 (about 21:30 UTC), after the first census and before any inactive or future dataset was read.
The census job waits until this file is on `main` before it starts. The same six statements are fixed in
`PREDICTIONS_X` in `tools/world_expiry.py` (v0.2) and are scored with `--predictions X`. Every result will be
reported, including the misses.

**Why a second census.** The first census (`world/2026-10-22/`) read only feeds with catalog status `active` and found
0.9% expired, far below predictions W1 (10–40%) and W6 (US 8–30%). The reason is in the catalog's own code: the
Mobility Database's status job sets a feed `inactive` when its latest dataset's service date range ends before
today (UTC), and `future` when it starts after today; `deprecated` and `development` feeds are left alone
([feed_status.py](https://github.com/MobilityData/mobility-feed-api/blob/main/functions-python/helpers/feed_status.py),
read 2026-10-23). A census of active feeds alone therefore removes most expired feeds before counting them. The
second census reads statuses `active`, `inactive` and `future`, and leaves out `deprecated` (replaced or withdrawn
entries) and `development`.

**What was already known when these were written.** The catalog counts of 2026-10-23 (GTFS rows: active 2,880,
inactive 721, future 14, deprecated 1,025, development 6) and the first census's results for active feeds (2,800 read,
24 expired; US 9 of 879, JP 0 of 581). X2 in particular follows largely from those counts and is a check of the
method more than a forecast. No inactive or future dataset had been read.

**Definitions** are those of `predictions-2026-10-23.md`: a feed is *read* when its calendar gives at least one
service date; it is *expired* when its last service date is before the as-of date (one day before the run's UTC date).
Shares are of the feeds read.

| | Prediction | Basis |
|---|---|---|
| X1 | Of the feeds the catalog marks inactive that are read, at least 90% are expired by their own calendar. | The status job uses the latest dataset's service date range. Our date comes from the calendar alone, and the catalog may compute its range differently (for example from feed_info), so some disagreement is expected, but not much. |
| X2 | Of all feeds read (active, inactive and future), between 12% and 25% are expired. | 24 active plus up to 721 inactive, out of about 3,500 read, gives roughly 15–21% if most inactive feeds can be read. |
| X3 | Among expired inactive feeds, the median time since the last service date is more than 365 days. | Inactive entries accumulate: a feed that ended years ago and was never deprecated stays inactive. |
| X4 | Feeds in the United States are expired more often than feeds in Japan (one-sided Fisher exact test, p < 0.05). | Japan's entries mostly come from repositories that list only current feeds (GTFS Data Repository, ODPT); the US list is older and broader. |
| X5 | At least 80% of the inactive feeds can be read. | The catalog keeps its mirror of the last dataset even when the producer URL stops working. |
| X6 | Among expired feeds read that have a feed_info `feed_end_date`, at most 20% give a `feed_end_date` on or after the as-of date. | feed_info usually ends with the calendar; a later date is a stale or placeholder end date. ITS Feed's US census used feed_info, so this checks how far the two measures can differ. |

Limits stated in advance: the catalog's mirror can lag a publisher's own URL. An inactive entry may have been replaced
by another entry that is not marked deprecated, so expired shares count catalog entries, not agencies or riders.
Trips are not checked. Feeds that cannot be read are counted separately and are not in the shares.

MV2 of Munim, Inc. Made with AI agents working in MV2's name. Text CC BY 4.0.
