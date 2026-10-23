# gtfs-world-expiry

How many of the world's catalogued public-transport timetables have run out of dates? This repository counts, for
every active GTFS Schedule feed in the [Mobility Database](https://mobilitydatabase.org/) catalog, the last date on
which any of its services runs, and how many feeds have no service left. Results are broken down by country and by
catalog source.

By MV2 of Munim, Inc. Made with AI agents working in MV2's name. Code Apache-2.0; results and text CC BY 4.0.

## Status

- **2026-10-23: method and predictions published, before any dataset was read.**
  [predictions-2026-10-23.md](predictions-2026-10-23.md) fixes six predictions (W1 to W6) and the definitions.
  The first census runs once that file is on `main`. Its results will go in `world/<as-of date>/` with every
  prediction scored, including the misses.

## Why

A rider-facing app that loads an expired timetable shows no buses, or wrong ones. Validators flag this one feed at a
time (MobilityData's `feed_expiration_date_7_days` and `_30_days` notices). ITS Feed counted the notices for 736 US
feeds in September 2026 ([article](https://its-feed.com/articles/what-the-gtfs-validator-checks/)). No worldwide,
country-by-country count was found (searched 2026-10-23). MV2's sister project
[gtfs-jp-lapses](https://github.com/munimtechnologies/gtfs-jp-lapses) measures the same thing in depth for Japan.

## Method

1. Take `feeds_v2.csv` from the Mobility Database (catalog metadata, CC0). Keep the rows with `data_type = gtfs` and
   `status = active`.
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

- The catalog's mirror can lag a publisher's own URL, and an entry marked active may have been replaced by another.
- Trips are not checked: a service with no trips still counts. Removed dates are checked only in the last 62 days of
  each calendar range. Services whose last 62 days are all removed are counted in `tail_cut`, not guessed.
- Countries are the catalog's. Counts are per catalog entry, not per agency or per rider.

## Files

- `predictions-2026-10-23.md`: the predictions, fixed before the first census.
- `tools/world_expiry.py`: the census (standard library only); `tools/test_world_expiry.py`: tests on made-up zips
  served from memory, with every expected value worked by hand. Both are committed separately, and only after the
  tests pass.

## Reproduce

```
python tools/test_world_expiry.py -v
curl -o feeds_v2.csv https://files.mobilitydatabase.org/feeds_v2.csv
python tools/world_expiry.py --catalog feeds_v2.csv --predictions --out out/world
```

Results go to `out/world/<as-of>/`: `feeds.csv` (one row per feed), `by_country.csv`, `summary.json` and
`summary.md`.

Source data: the Mobility Database by MobilityData (catalog metadata CC0 1.0). Each dataset belongs to its
publisher.
