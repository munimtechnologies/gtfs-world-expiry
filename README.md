# gtfs-world-expiry

How many of the world's catalogued public-transport timetables have run out of dates? This repository counts, for
GTFS Schedule feeds in the [Mobility Database](https://mobilitydatabase.org/) catalog, the last date on which any of
their services runs, and how many feeds have no service left. Results are broken down by catalog status, country and
catalog source.

By MV2 of Munim, Inc. Made with AI agents working in MV2's name. Code Apache-2.0; results and text CC BY 4.0.

## Status

- **2026-10-23: second census (active, inactive and future feeds), `world/2026-10-22-all/`.** 3,615 feeds; 3,502
  read; 698 (19.9%) have no service left, 392 of them for more than a year. All six pre-registered predictions (X1 to
  X6) held. 38 entries have a catalog status that disagrees with their own calendar, for two different reasons
  (below).
- **2026-10-23: follow-up pre-registered.** [predictions-y-2026-10-23.md](predictions-y-2026-10-23.md) fixes six
  predictions (Y1 to Y6) on what happens to those 38 entries a week later. The follow-up census will be run on or
  after 2026-10-30 and compared with `tools/world_diff.py`.
- **2026-10-23: first census (active feeds only), `world/2026-10-22/`.** 2,800 of 2,880 active feeds read; 24
  expired (0.9%). Three of six predictions held. The low share was a flaw in the method, explained below.

## Second census: results

As of 2026-10-22 (catalog file read 2026-10-23 at about 21:16 UTC), the catalog listed 3,615 GTFS feeds with status
`active` (2,880), `inactive` (721) or `future` (14). 3,502 could be read (69 had no mirrored dataset, 25 no service
dates, 14 no calendar, 5 a broken zip). Full tables: [summary.md](world/2026-10-22-all/summary.md); one row per feed:
[feeds.csv](world/2026-10-22-all/feeds.csv).

| catalog status | feeds | read | expired | expired share | expired over 1 year |
|---|---|---|---|---|---|
| all | 3,615 | 3,502 | 698 | 19.9% | 392 |
| active | 2,880 | 2,800 | 24 | 0.9% | 12 |
| inactive | 721 | 688 | 674 | 98.0% | 380 |
| future | 14 | 14 | 0 | 0.0% | 0 |

Predictions ([predictions-v2-2026-10-23.md](predictions-v2-2026-10-23.md), recorded before any inactive or future
dataset was read):

| | Prediction | Result |
|---|---|---|
| X1 | at least 90% of inactive feeds read are expired by their own calendar | 98.0% (674 of 688), held |
| X2 | 12–25% of all feeds read are expired | 19.9%, held |
| X3 | median time since the last service day of expired inactive feeds over 365 days | 510 days, held |
| X4 | US feeds expired more often than Japanese ones (one-sided Fisher exact, p < 0.05) | US 28.8% (354 of 1,230), JP 7.6% (48 of 629), p = 4.6e-29, held |
| X5 | at least 80% of inactive feeds can be read | 95.4%, held |
| X6 | at most 20% of expired feeds with a feed_info end date give one on or after the as-of date | 5.9%, held |

As the predictions file said in advance, X1 and X2 follow largely from how the catalog sets its status and are checks
of the method more than forecasts. X3 to X6 are about the feeds themselves.

**Countries and sources (exploratory, not predicted).** Among countries with at least 30 feeds read, the expired share
is highest in Poland (32.0%, 16 of 50), the US (28.8%), Australia (25.0%, 9 of 36), Portugal (25.0%) and Germany
(23.8%), and lowest in Sweden (9.6%, 5 of 52), Japan (7.6%) and Great Britain (4.8%, 2 of 42). By the catalog source of
the entry (id prefix), entries imported from the US National Transit Database (`ntd-`) are expired most often
(42.5%, 60 of 141), then `mdb-` (25.0%), `tld-` (22.3%), France's `tdg-` (9.9%), `odpt-` (8.9%) and Japan's
`jbda-` (7.4%). Entries are not agencies: some feeds appear twice (for example `mdb-176` and `mdb-3211` serve the
same file). These counts were found after the census and get no claim beyond what they are.

### When the catalog status and the calendar disagree

38 of the 3,488 active or inactive entries read (1.1%) have a status that disagrees with their own calendar. We
checked ten of them by hand on their catalog pages on 2026-10-23. They show two different mechanisms.

**Active, but no service left (24 entries): mostly datasets with no service date range.** 19 ended 30 days or more
before the as-of date, 12 of them more than a year before. Of the 7 we checked, 6 show no service date range for
their latest dataset ("–"): `mdb-2234` (Camarillo Area Transit, US, calendar ends 2021-12-31), `tld-5769`
(Kanawha Valley Regional Transportation Authority, US, 2024-06-21), `mdb-912` (Miccolis, IT, 2022-12-31), `mdb-3470`
(Marne Bois Bateau Bus, FR, 2026-10-18), `tdg-83969` (Réseau urbain Yolé, FR, 2026-09-30) and `tdg-84018` (Bacs
Ecouflant/Cantenay-Epinard et Pruillé, FR, 2026-09-27). The status job only looks at datasets that have both ends of
the range, so these entries stay `active` however long ago their service ended. The 7th, `mdb-176` (Rocky Mountain
National Park shuttles, seasonal), has a range ending 2026-10-20 and had simply not been updated yet.

**Inactive, but service left (14 entries): a status that had not caught up with a new dataset.** All three we checked
had received a new dataset shortly before the catalog file was read, and their pages show an "Active" label beside
the new range, while `feeds_v2.csv` still listed them as `inactive`: `mdb-3149` (Shore Transit, US; new dataset
downloaded 2026-10-20, service 2026-09-07 to 2027-05-28), `mdb-1956` (Warrington's Own Buses, GB; a file replaced
every week, new dataset 2026-10-20 after the previous one ended 2026-10-18) and `tdg-82148` (Réseau urbain Citéa, FR;
new dataset 2026-10-23). We do not know how often the catalog file is exported or the status job runs, so the
length of this lag is not measured yet. The follow-up census is meant to measure it.

What this means for users of the catalog: filtering on `status = active` keeps a small number of long-dead feeds
(those with no recorded range) and drops a few live ones (recently renewed). Reading the dataset's own calendar
avoids both.

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
This was not checked before the census. That is our error, and the misses stand as recorded. The second census
(above) reads inactive and future feeds too.

**What still holds.** The end-day pattern does not depend on the status filter. Among active feeds ending within a
year, 17.8% end on 12-31 and 12.9% on 03-31. In Japan, 51.4% end on 03-31, the end of the fiscal year. In the US,
02-01 (7.1%) and 03-01 (6.0%) follow 12-31 (15.3%).

## Why

A rider-facing app that loads an expired timetable shows no buses, or wrong ones. Validators flag this one feed at a
time (MobilityData's `feed_expiration_date_7_days` and `_30_days` notices). ITS Feed counted the notices for 736 US
feeds in September 2026 ([article](https://its-feed.com/articles/what-the-gtfs-validator-checks/)). No worldwide,
country-by-country count was found (searched 2026-10-23), and we found no earlier check of how often the catalog's
status disagrees with the feeds' own calendars. MV2's sister project
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
5. `tools/world_diff.py` compares two censuses. It follows the entries whose status disagreed with their calendar in
   the first one and reports whether they agree in the second, plus every status move between the two files.

The census publishes only dates and counts derived from each feed. Feed contents stay under their publishers'
licences and are not redistributed.

## Limits

- The catalog's mirror can lag a publisher's own URL, and an entry may have been replaced by another.
- Trips are not checked: a service with no trips still counts. Removed dates are checked only in the last 62 days of
  each calendar range. Services whose last 62 days are all removed are counted in `tail_cut`, not guessed.
- Countries are the catalog's. Counts are per catalog entry, not per agency or per rider, and a few files are
  catalogued twice.
- The hand checks cover 10 of the 38 disagreeing entries.

## Files

- `predictions-2026-10-23.md`, `predictions-v2-2026-10-23.md`, `predictions-y-2026-10-23.md`: the predictions,
  each fixed before the census it scores.
- `world/2026-10-22/`: the first census (active only). `world/2026-10-22-all/`: the second census (active, inactive,
  future). Each has `feeds.csv` (one row per feed), `by_country.csv`, `summary.json` and `summary.md`.
- `tools/world_expiry.py`: the census (standard library only); `tools/test_world_expiry.py`: tests on made-up zips
  served from memory, with every expected value worked by hand. `tools/world_diff.py` and
  `tools/test_world_diff.py`: the comparison of two censuses. Tools are committed only after their tests pass.

## Reproduce

```
python tools/test_world_expiry.py -v
python tools/test_world_diff.py -v
curl -o feeds_v2.csv https://files.mobilitydatabase.org/feeds_v2.csv
python tools/world_expiry.py --catalog feeds_v2.csv --statuses active,inactive,future --predictions X --out out/world
python tools/world_diff.py --before world/2026-10-22-all/feeds.csv --after out/world --predictions Y --out out/diff
```

Results go to `<out>/<as-of>/`: `feeds.csv` (one row per feed, with its catalog status), `by_country.csv`,
`summary.json` and `summary.md`. The catalog changes daily, so a later run gives different counts.

Source data: the Mobility Database by MobilityData (catalog metadata CC0 1.0). Each dataset belongs to its
publisher.
