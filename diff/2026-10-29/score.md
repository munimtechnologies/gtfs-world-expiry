# Scoring of the status-lag follow-up (Y1 to Y6)

MV2 of Munim, Inc. Made with AI agents working in MV2's name. Text CC BY 4.0.

Predictions: [predictions-y-2026-10-23.md](../../predictions-y-2026-10-23.md), written on 2026-10-23 before the
follow-up census. The follow-up ran on 2026-10-30 from 01:13 to 01:27 UTC (job `world-followup-v1`) with the same
tool and settings as the second census: the Mobility Database's `feeds_v2.csv` was downloaded at the start of the
run, every `active`, `inactive` and `future` GTFS entry was read (as-of date 2026-10-29), and `tools/world_diff.py`
compared it with `world/2026-10-22-all/feeds.csv` (catalog file read 2026-10-23 at about 21:16 UTC). The verdicts
are the tool's own ([diff.md](diff.md)); none was changed by hand.

| | Prediction | Result | Verdict |
|---|---|---|---|
| Y1 | Of the 14 `inactive_running` entries, at least 60% agree in the follow-up census. | 0 of 14 | **did not hold** |
| Y2 | Of the 19 `active_stuck` entries, at least 80% still disagree. | 19 of 19 | **held** |
| Y3 | All six hand-checked entries with no service date range still disagree. | 6 of 6 | **held** |
| Y4 | `mdb-176` and `mdb-3211` (seasonal, range ended 2026-10-20) agree. | 0 of 2 | **did not hold** |
| Y5 | Between 15 and 40 active entries have no service left. | 30 | **held** |
| Y6 | Between 3 and 40 inactive entries still have service left. | 18 | **held** |

Every entry followed was still in the catalog file and was read in both censuses; none left the file.

## What the misses show: no status changed at all

The predictions assumed the catalog's status job runs often, so that a status out of step with a new or ended
dataset would catch up within a week. It did not, for any entry. Between the two reads of `feeds_v2.csv`, about six
days apart, **not one of the 3,615 GTFS entries changed status**: 2,880 stayed `active`, 721 `inactive` and 14
`future`. The datasets behind them did change. Among the 38 entries followed, `mdb-1956` (Warrington's Own Buses, a
file replaced every week) now has a latest dataset that runs to 2026-11-01 instead of 2026-10-25, and still shows
`inactive`; `mdb-2819`'s latest dataset changed too. `mdb-176` and `mdb-3211`, whose catalog page showed a service
date range ending 2026-10-20 when we checked it on 2026-10-23, were still `active` on 2026-10-30.

So Y1 and Y4 failed for one shared reason: between 2026-10-23 and 2026-10-30, the status column of `feeds_v2.csv`
did not move. The disagreements grew instead. In the second census 38 entries disagreed with their own calendars;
in the follow-up 48 do (18 inactive with service left, 21 active with none for 30 days or more, 9 active with none
for less).

How the status is meant to be set: the Mobility Database's `update_feed_status` function
([feed_status.py](https://github.com/MobilityData/mobility-feed-api/blob/main/functions-python/helpers/feed_status.py))
sets each feed from the service date range of its latest dataset. It is started by an HTTP request, and
[mobility-feed-api#879](https://github.com/MobilityData/mobility-feed-api/issues/879) (closed 2025-03-06) asked for
it to run daily. The CSV export (`functions-python/export_csv`) writes each feed's stored status. Neither file shows
the schedule. From outside we cannot tell whether the status function did not run in this week or its results did
not reach the CSV. We only see that the CSV's statuses did not change. A week is one observation. We have not
measured how long statuses had been frozen before 2026-10-23.

## What held

Y2, Y3 and Y5: entries whose latest dataset has no service date range stay `active` however long ago their service
ended. **This mechanism was already known, and our 2026-10-23 write-up missed it.**
[mobility-feed-api#1209](https://github.com/MobilityData/mobility-feed-api/issues/1209) (opened 2025-05-22)
reports that the status query skips datasets without both range dates, and maintainers agreed such feeds should be
treated as `inactive`. A fix, [mobility-feed-api#1826](https://github.com/MobilityData/mobility-feed-api/pull/1826),
has been open since 2026-09-03. Our counts add only the number of entries affected on given dates.

Y6 held: 18 inactive entries still have service left, against 14 a week earlier.

## Re-check of the census predictions (reported, not a new test)

The tool also re-scored the second census's predictions X1 to X6 on the new data. All six hold again: 3,503 of 3,615
entries read, 700 (20.0%) with no service left (395 for more than a year), 97.4% of inactive entries read have no
service left, and the US share stays far above Japan's (28.7% against 7.6%). Full tables:
[summary.md](../../world/2026-10-29/summary.md).

## Limits

Both censuses read the catalog's mirror of each latest dataset, not the producer's URL, and service dates come from
`calendar.txt` and `calendar_dates.txt` only. Hand checks: 10 of the 38 entries disagreeing on 2026-10-23 were checked
on their catalog pages; none of the 10 new ones has been checked. Some entries are the same file catalogued twice
(`mdb-176` and `mdb-3211`).
