# gtfs-world-expiry

How many of the world's catalogued public-transport timetables have run out of dates? This repository counts, for
GTFS Schedule feeds in the [Mobility Database](https://mobilitydatabase.org/) catalog, the last date on which any of
their services runs, and how many feeds have no service left. Results are broken down by catalog status, country and
catalog source.

By MV2 of Munim, Inc. Made with AI agents working in MV2's name. Code Apache-2.0; results and text CC BY 4.0.

## Status

- **2026-10-23: first census (active feeds only), `world/2026-10-22/`.** 2,880 active feeds; 2,800 read; 24 expired
  (0.9%). Three of six predictions held. The low share is mostly a flaw in the method, not a finding about feeds
  (see below).
- **2026-10-23: second census pre-registered.** [predictions-v2-2026-10-23.md](predictions-v2-2026-10-23.md) fixes
  six predictions (X1 to X6) for a census of active, inactive and future feeds, before any inactive or future dataset
  is read. Its results will go in `world/<as-of date>/`, with every prediction scored.

## First census: results and what went wrong

As of 2026-10-22, of 2,880 GTFS feeds with catalog status `active`, 2,800 could be read (55 had no mirrored
dataset, 15 no service dates and 10 no calendar). By their own calendars, 24 (0.9%) have no service left, 12 of them
for more than a year ([summary.md](world/2026-10-22/summary.md)). Another 140 end within 30 days.

Predictions ([predictions-2026-10-23.md](predictions-2026-10-23.md), recorded before any dataset was read):

| | Prediction | Result |
|---|---|---|
| W1 | 10–40% of active feeds expired | 0.9%, **missed** |
| W2 | `tfs-` feeds expired more often than `mdb-` | **could not be tested**: no active feed has a `tfs-` id in the catalog of 2026-10-23 (the tool's report says "did not hold"; that is wrong, there was nothing to test) |
| W3 | Japan at most 3% expired | 0.0% (0 of 581), held |
| W4 | most common last day 12-31, at least 10% | 12-31, 17.8% of 2,341, held |
| W5 | Japan: at least 25% end on 03-31 | 51.4% of 558, held |
| W6 | US 8–30% expired | 1.0% (9 of 879), **missed** |

**Why W1 and W6 missed: the census filtered out what it meant to count.** The catalog's status is not set by hand.
The Mobility Database's status job
([feed_status.py](https://github.com/MobilityData/mobility-feed-api/blob/main/functions-python/helpers/feed_status.py))
sets a feed `inactive` when the service date range of its latest dataset ends before today (UTC), `future` when it
starts after today, and `active` otherwise; `deprecated` and `development` feeds are left alone. Keeping only
`active` rows therefore removed most expired feeds before they were counted: the same catalog had 721 GTFS feeds
marked `inactive`. The predictions assumed that `active` meant "maintained", as in the catalog schema's older wording.
This was not checked before the census. That is our error, and the misses stand as recorded.

**What the 24 are.** They are active entries whose calendar has ended anyway. Two were checked by hand on their
catalog pages on 2026-10-23:
- `mdb-2234` (Camarillo Area Transit, US): calendar ends 2021-12-31. The catalog page shows no service date range
  ("–"). The status job skips datasets without a range, so the entry stays `active`.
- `mdb-176` (Rocky Mountain National Park shuttles, US, seasonal): calendar ends 2026-10-20, two days before the as-of
  date. The catalog page shows the same end date. The status had not caught up yet when the catalog file was read.

The others were not checked one by one. Twelve ended more than a year ago, five ended 2 to 25 days before the as-of
date (probably a status not yet updated, as for `mdb-176`; not checked), and seven ended 110 to 361 days before it. The list is in [feeds.csv](world/2026-10-22/feeds.csv) (`class` = `expired` or `expired_over_1y`).

**What still holds.** The end-day pattern does not depend on the status filter. Among active feeds ending within a
year, 17.8% end on 12-31 and 12.9% on 03-31. In Japan, 51.4% end on 03-31, the end of the fiscal year. In the US,
02-01 (7.1%) and 03-01 (6.0%) follow 12-31 (15.3%).

## Why

A rider-facing app that loads an expired timetable shows no buses, or wrong ones. Validators flag this one feed at a
time (MobilityData's `feed_expiration_date_7_days` and `_30_days` notices). ITS Feed counted the notices for 736 US
feeds in September 2026 ([article](https://its-feed.com/articles/what-the-gtfs-validator-checks/)). No worldwide,
country-by-country count was found (searched 2026-10-23). MV2's sister project
[gtfs-jp-lapses](https://github.com/munimtechnologies/gtfs-jp-lapses) measures the same thing in depth for Japan.

## Method

1. Take `feeds_v2.csv` from the Mobility Database (catalog metadata, CC0). Keep the rows with `data_type = gtfs` and
   the chosen statuses (`--statuses`, default `active`; the second census uses `active,inactive,future`).
2. For each one, open the catalog's mirror of its latest dataset (`urls.latest`) with HTTP range requests. Read only
   `calendar.txt`, `calendar_dates.txt` and `feed_info.txt`. A typical feed costs three or four small requests.
   Requests come from four workers, each pausing after every feed.
3. The last service date is the latest date on which some service runs. That is either a flagged weekday inside a
   `calendar.txt` range that `calendar_dates.txt` does not remove, or a date added in `calendar_dates.txt`.
4. A feed is expired when that date is before the as-of date. The as-of date is one day before the UTC run date,
   so it has passed in every time zone. The other classes are: ends within 30 days, ends within a year, and ends
   after more than a year.

The census publishes only dates and counts derived from each feed. Feed contents stay under their publishers'
licences and are not redistributed.

## Limits

- The catalog sets `inactive` from its own service date range, so a census of `active` feeds alone undercounts
  expiry (above). The second census reads inactive and future feeds too.
- The catalog's mirror can lag a publisher's own URL, and an entry may have been replaced by another.
- Trips are not checked: a service with no trips still counts. Removed dates are checked only in the last 62 days of
  each calendar range. Services whose last 62 days are all removed are counted in `tail_cut`, not guessed.
- Countries are the catalog's. Counts are per catalog entry, not per agency or per rider.

## Files

- `predictions-2026-10-23.md`, `predictions-v2-2026-10-23.md`: the predictions, each fixed before the census it
  scores.
- `world/2026-10-22/`: the first census (`feeds.csv` one row per feed, `by_country.csv`, `summary.json`,
  `summary.md`).
- `tools/world_expiry.py`: the census (standard library only); `tools/test_world_expiry.py`: tests on made-up zips
  served from memory, with every expected value worked by hand. Tools are committed only after the tests pass.

## Reproduce

```
python tools/test_world_expiry.py -v
curl -o feeds_v2.csv https://files.mobilitydatabase.org/feeds_v2.csv
python tools/world_expiry.py --catalog feeds_v2.csv --predictions W --out out/world
python tools/world_expiry.py --catalog feeds_v2.csv --statuses active,inactive,future --predictions X --out out/world2
```

Results go to `<out>/<as-of>/`: `feeds.csv` (one row per feed, with its catalog status from v0.2), `by_country.csv`,
`summary.json` and `summary.md`. The catalog changes daily, so a later run gives different counts.

Source data: the Mobility Database by MobilityData (catalog metadata CC0 1.0). Each dataset belongs to its
publisher.
