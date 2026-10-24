# gtfs-world-expiry

How many of the world's catalogued public-transport timetables have run out of dates? This repository counts, for
GTFS Schedule feeds in the [Mobility Database](https://mobilitydatabase.org/) catalog, the last date on which any of
their services runs, and how many feeds have no service left. Results are broken down by catalog status, country and
catalog source. A second tool checks how closely the catalog's copies of Japanese feeds follow the national
repository they come from, and a third compares the catalog's copies worldwide with the files the producers serve
themselves.

By MV2 of Munim, Inc. Made with AI agents working in MV2's name. Code Apache-2.0; results and text CC BY 4.0.

## Status

- **2026-10-24: all 17 stale copies checked by hand (v0.4.1).** Every catalog page shows the producer host we read,
  a latest stored download on the day we recorded, and no download error. The last downloads range from 2024-09-02 to
  2026-07-08. For 12 of the 17 the evidence that downloads stopped while the producer kept publishing is strong; for
  5 we cannot tell when the producer's newer file appeared
  ([hand-checks.md](source/2026-10-23/hand-checks.md)).
- **2026-10-24: follow-up pre-registered.** [predictions-t-2026-10-24.md](predictions-t-2026-10-24.md) fixes four
  predictions (T1 to T4) for a run on or after 2026-10-30 that checks every live entry against its producer: are the
  17 stale copies still stale a week later, and how many entries whose copy still runs have a stalled download? It is
  scored by `tools/stall_check.py`.
- **2026-10-24: source check run, `source/2026-10-23/` (v0.4.0).** All five pre-registered predictions (S1 to S5)
  held. Of 698 catalog entries whose copy has no service left, 479 producer files could be read: 461 (96.2%) are the
  same file, so the timetable has really ended at the source, and 17 (3.5%) are **stale copies**: the producer serves a
  newer timetable that still runs, which the catalog has not stored.
- **2026-10-24: correction to the mirror check (v0.3.1).** The v0.3.0 write-up said 13 Japanese entries were stale
  mirrors of feeds the repository still serves a valid file for. That was wrong. All 13 hold exactly the repository's
  current file; the file's own calendar has ended, but the repository's listed validity dates run past it. No stale
  mirror was found among the 43 entries. Details under "Correction" below; the data and the M4 score are unchanged.
- **2026-10-24: mirror check run, `mirror/2026-10-24/`.** 584 catalog entries that mirror Japan's GTFS Data
  Repository were compared with the files the repository serves itself. Four of five pre-registered predictions
  (M1 to M5) held. 97.8% of active entries hold the repository's current file, no entry carries a timetable the
  repository has only published for a later date, and 99.6% of the repository's open active feeds have an entry.
  M4 missed: of 43 entries whose copy has no service left, 30 (69.8%, predicted at least 75%) have no file in force
  at the repository either by its listed dates. The other 13 are files whose own calendar ended before the date the
  repository lists (see the correction).
- **2026-10-23: second census (active, inactive and future feeds), `world/2026-10-22-all/`.** 3,615 feeds; 3,502
  read; 698 (19.9%) have no service left, 392 of them for more than a year. All six pre-registered predictions (X1 to
  X6) held. 38 entries have a catalog status that disagrees with their own calendar, for two different reasons
  (below).
- **2026-10-23: follow-up pre-registered.** [predictions-y-2026-10-23.md](predictions-y-2026-10-23.md) fixes six
  predictions (Y1 to Y6) on what happens to those 38 entries a week later. The follow-up census will be run on or
  after 2026-10-30 and compared with `tools/world_diff.py`.
- **2026-10-23: first census (active feeds only), `world/2026-10-22/`.** 2,800 of 2,880 active feeds read; 24
  expired (0.9%). Three of six predictions held. The low share was a flaw in the method, explained below.

## Source check: the catalog's copy against the producer's own file (results)

The catalog serves its own copy of each feed's latest dataset (`urls.latest`) and records where the producer
publishes it (`urls.direct_download`). `tools/source_check.py` reads every copy and then, for each entry whose copy
has no service left (the expired group), the producer's file. As a control it does the same for a seeded random
sample of 300 entries whose copy still has service. Two files are the same when they hold the same `.txt` members with
the same CRC-32 and size. A **stale copy** is an expired-group entry whose producer serves a different file that still
has service. Producer URLs that need a key are not read, and each producer host is sent at most one new file request
per second.

The check ran on 2026-10-24 between 04:52 and 05:14 UTC, with the as-of date 2026-10-23, on the 3,615 entries with
status `active`, `inactive` or `future`. Full tables: [summary.md](source/2026-10-23/summary.md); one row per entry:
[sources.csv](source/2026-10-23/sources.csv); hand checks and exploratory counts:
[hand-checks.md](source/2026-10-23/hand-checks.md).

| | expired group (698) | control group (300) |
|---|---|---|
| same file at the producer | 461 | 239 |
| producer's file differs and still runs | 17 (stale copies) | 8 |
| producer's file differs and has ended too | 1 | 0 |
| producer URL could not be read | 196 (HTTP 404: 105) | 32 |
| producer URL needs a key (not read) | 23 | 21 |

| | Prediction (fixed before any producer file was read) | Result |
|---|---|---|
| S1 | 35–85% of expired-group producer URLs that need no key return a readable zip with service dates | 71.0% (479 of 675), held |
| S2 | at most 15% of expired-group entries whose producer file is read are stale copies | 3.5% (17 of 479), held |
| S3 | at least 80% of expired-group entries whose producer file has also ended hold the same file as the copy | 99.8% (461 of 462), held |
| S4 | at least 80% of control-group entries whose producer file is read hold the same file as the copy | 96.8% (239 of 247), held |
| S5 | HTTP 404 is the most common failure among expired-group producer URLs that cannot be read | 105 of 196, held |

**What it means.** When the catalog marks a feed `inactive` because its copy has run out, that is almost always
true at the source: 461 of the 479 producer files we could read are the very same expired file. The predictions were
loose, and all five held.

**The 17 stale copies.** These are entries the catalog shows as expired and `inactive` although the producer publishes
a valid timetable at the URL the catalog records. They include MARTA (Atlanta), Metro St. Louis, the Milwaukee County
Transit System, Kitsap Transit, Sun Metro (El Paso), Loudoun County Transit, Blacksburg Transit, Tampere (Finland),
Metro de Málaga, AMT Genova, SKM Tricity rail (Poland), Szeged and Veszprém (Hungary); the full list is in
[summary.md](source/2026-10-23/summary.md). The catalog's copy had run out a median of 108 days before the as-of date
(18 to 1,756 days), and the producer's file runs a median of 182 days beyond it.

We checked all 17 by hand on their catalog pages on 2026-10-24
([hand-checks.md](source/2026-10-23/hand-checks.md)). Each page lists a producer URL on the host we read and a latest
stored download on the day we recorded, and none shows a download error, although the catalog checks producer URLs
daily. The last downloads range from 2024-09-02 (Alice Springs, Australia) to 2026-07-08 (Szeged). The evidence that
the downloads stopped while the producer kept publishing is strong for 12: nine producers (among them MARTA, Málaga,
Milwaukee and AMT Genova) had the newer file on their server 5 to 93 days before the as-of date by their
Last-Modified header, and three that republish often were stored every day (SKM, until 2026-06-18), every week (Metro
St. Louis, until 2026-05-29) or every one to four weeks (Tampere, until 2026-05-13) and never after. For the other 5
(Loudoun, Alice Springs, Szeged, High Point and Hinton) the producer sends no Last-Modified header, so the copy is stale
but we cannot tell when the newer file appeared.

We do not know why the downloads stopped. MobilityData is already working on download failures that do not reproduce
by hand ([mobility-feed-api#1860](https://github.com/MobilityData/mobility-feed-api/issues/1860)) and on Málaga's URL
([mobility-database-catalogs#1618](https://github.com/MobilityData/mobility-database-catalogs/issues/1618)). Alice
Springs was reported in 2024 as serving an HTML page to scripted downloads
([mobility-feed-api#502](https://github.com/MobilityData/mobility-feed-api/issues/502), closed); its page lists two
downloads after that and none since. We found no public issue for the other stale copies (searched 2026-10-24).

**Exploratory, not predicted.** 10 of the 17 stale copies were stored between 2026-04-19 and 2026-06-18, against 16 of
the 461 entries whose producer serves the same file. In 9 of the 12 stale cases whose producer sends a Last-Modified
header, the newer file had been on the server for 5 to 93 days. The 8 differing files in the control group are not
stale: the catalog stored all 8 copies between 2026-10-22 and 2026-10-24, and their producer files run at most 9 days
longer.

Why it matters: a feed whose catalog copy has ended is marked `inactive` and drops out of most uses of the catalog.
When its producer still publishes a valid timetable, riders of apps that rely on the catalog lose a service that
exists. The nearest earlier check we found, ITS Feed's September 2026 download of 828 US entries not marked inactive,
counted producer URLs that return no zip. It did not compare the files or look at expired entries.

## Mirror check: the catalog's copies of Japanese feeds (results)

The Mobility Database imports Japan's [GTFS Data Repository](https://gtfs-data.jp/) as entries whose ids start with
`jbda-`. Each entry points at the repository's download URL, and the catalog keeps its own copy of the latest file
(`urls.latest`), which is what users of the catalog download. The repository can serve several files per feed: the
one in force (`rid=current`), and timetables already published for later dates (`rid=next_1`, ...; `rid=next` gives
the next file if there is one). The catalog entry we checked by hand downloads `rid=current`, and the catalog's
[FAQ](https://mobilitydatabase.org/faq) says it checks producer URLs for updates every day at midnight UTC.

`tools/mirror_check.py` compares, for every `jbda-` entry, the catalog's copy with the repository's current file:
the same `.txt` files with the same CRC-32 and size count as the same file, however the zip was packed. When they
differ it tries the repository's next and previous files. It also reads each feed's API entry once, to see when the
current file came into force, whether a later file is published, and whether the feed is discontinued, and it lists
the repository feeds that have no catalog entry. Only zip directories and the calendar files are read, through HTTP
range requests, with a pause of one second before every request to the repository.

As of 2026-10-24 (Japan time), the catalog listed 584 `jbda-` GTFS entries (539 `active`, 45 `inactive`). Every one
downloaded `rid=current`; 580 matched a listed repository feed and 4 a feed the repository no longer lists. Full
tables: [summary.md](mirror/2026-10-24/summary.md); one row per entry: [mirror.csv](mirror/2026-10-24/mirror.csv).

| | Prediction | Result |
|---|---|---|
| M1 | at least 85% of active entries (both files read) hold the repository's current file | 97.8% (525 of 537), held |
| M2 | no entry holds a later (`next_1`) file, though some feeds have one published | 0 of 20 feeds with a later file, held |
| M3 | at least 90% of the repository's open, active feeds have an entry | 99.6% (551 of 553), held |
| M4 | at least 75% of entries whose copy has no service left have none at the repository either | 69.8% (30 of 43), **missed** |
| M5 | at most 5% of active entries belong to a discontinued or delisted feed | 0.4% (2 of 539), held |

**What held.** The catalog's copy is the repository's current file for all but 12 of 539 active entries, and
timetables the repository publishes ahead of time do not reach the catalog early. 20 repository feeds had a later file
already published (a median of 18 days before it starts, as
[gtfs-jp-lapses](https://github.com/munimtechnologies/gtfs-jp-lapses) also found), and the mirror held none of them: a
rider taking a Japanese feed from the global catalog sees a new timetable only on its first day, not when the operator
publishes it. The 12 active entries that were not on the current file were all files the repository had re-published
within the last day. Eight were Sanco (Mie Kotsu) feeds whose new `current` was published the same morning the check
ran, and the others were only hours old, so the daily mirror had not yet caught up. Among entries holding the current
file, the mirror was written a median of 0 days after the file took effect (quartiles 0 to 1).

**What missed (M4).** 43 entries have a mirrored copy with no service left on the as-of date. The tool counts the
repository as "running" when its API lists a current file whose dates cover the as-of date. By that rule, 30 have none
and 13 do, so M4 missed as recorded.

**Correction (2026-10-24).** Our v0.3.0 write-up read those 13 as stale mirrors: copies that had expired while the
repository served a newer, valid file. `mirror.csv` shows otherwise. All 13 have `holds = current`: the catalog's copy
is byte-for-byte the repository's current file (the same members, CRC-32 and sizes), and `source_last` equals
`mirror_last`. What differs is the repository's listing. Each file's own calendar ended before the date the repository
lists for it:

- 10 Nakatsu City (中津市) route feeds: listed in force to 2026-10-31, but the calendar ends between 2026-09-24 and
  2026-09-30.
- 王滝村 (Otaki Village): listed to 2027-03-31; the calendar ends 2026-10-12.
- 西脇市 (Nishiwaki City) and 南部町 (Nanbu Town): listed in force 2026-04-01 to 2027-03-31, but the file holds the
  previous fiscal year's calendar (2025-04-01 to 2026-03-31).

The 14th entry holding the current file (四万十市 demand-responsive transport) is discontinued at the repository. The
other 29 have no current file at the repository any more: 26 answer HTTP 404 and 3 are no longer listed. So **none of
the 43 is a stale mirror**. In every case the catalog's copy faithfully reflects what the repository serves. The 13 are
the repository's listed dates overstating the file, a pattern MV2's
[gtfs-jp-lapses](https://github.com/munimtechnologies/gtfs-jp-lapses) calendar-gap check already counts in Japan. The
data and the M4 score are unchanged; only the explanation was wrong. The tool's summary line "the repository's
current file still runs" should be read as "the repository lists a current file in force". The worldwide source check
(above) reached the same split for these 43 entries by a different route: 14 same file, 29 unreadable.

Two open, active repository feeds had no catalog entry at all ([missing.csv](mirror/2026-10-24/missing.csv)):
`hitachinakacity/Hitachinaka-smileaozorabus` and `hidakavillage/GTFS-Hidakavill_Bus`.

The five predictions were fixed before any file was read
([predictions-m-2026-10-24.md](predictions-m-2026-10-24.md)). Why it matters: a timetable published weeks ahead helps
only the users who can see it before it starts, and a listing that outlives its file tells riders a timetable is in
force when it has run out.

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
(those with no recorded range) and drops a few live ones (recently renewed, or stale copies, above). Reading the
dataset's own calendar avoids the first; only the producer's own file reveals the second.

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
status disagrees with the feeds' own calendars, of how closely its copies follow a national repository, or of how
many of its expired copies have a live file at the producer (searched 2026-10-24; MobilityData's issues discuss
single feeds). MV2's sister project [gtfs-jp-lapses](https://github.com/munimtechnologies/gtfs-jp-lapses) measures
expiry in depth for Japan.

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
6. `tools/mirror_check.py` compares the catalog's copies of `jbda-` feeds with the GTFS Data Repository (above). Its
   as-of date is the run day in Japan time.
7. `tools/source_check.py` compares the catalog's copies with the producers' own files worldwide (above). Its as-of
   date is the census's.

The census publishes only dates and counts derived from each feed. Feed contents stay under their publishers'
licences and are not redistributed.

## Limits

- The catalog's mirror can lag a publisher's own URL, and an entry may have been replaced by another.
- Trips are not checked: a service with no trips still counts. Removed dates are checked only in the last 62 days of
  each calendar range. Services whose last 62 days are all removed are counted in `tail_cut`, not guessed.
- Countries are the catalog's. Counts are per catalog entry, not per agency or per rider, and a few files are
  catalogued twice.
- The hand checks cover 10 of the 38 disagreeing entries.
- The mirror check reads each file once on one day and compares only the repository's current, next and previous
  files. It takes the mirror's `Last-Modified` header as the day the catalog stored its copy. Its "running" test uses
  the repository's listed dates, not the file's calendar.
- The source check reads each producer URL once, from one place. A producer can serve its URL differently to the
  catalog's fetcher than to ours, and files that differ only in non-calendar members count as different. It finds a
  stalled download only once the catalog's copy has run out: an entry whose downloads stopped but whose copy still
  runs is not counted. It takes the mirror's `Last-Modified` header as the day the catalog stored its copy; for all 17
  stale copies, checked by hand, that matched the latest download on the catalog page. The hand checks compare the
  producer's host, not the full URL, and the catalog pages list at most ten downloads.

## Files

- `predictions-2026-10-23.md`, `predictions-v2-2026-10-23.md`, `predictions-y-2026-10-23.md`,
  `predictions-m-2026-10-24.md`, `predictions-s-2026-10-24.md`, `predictions-t-2026-10-24.md`: the predictions,
  each fixed before the run it scores.
- `world/2026-10-22/`: the first census (active only). `world/2026-10-22-all/`: the second census (active, inactive,
  future). Each has `feeds.csv` (one row per feed), `by_country.csv`, `summary.json` and `summary.md`.
- `mirror/2026-10-24/`: the mirror check against the GTFS Data Repository: `mirror.csv` (one row per `jbda-` entry),
  `missing.csv` (repository feeds with no entry), `summary.json` and `summary.md`.
- `source/2026-10-23/`: the source check against producers' own files: `sources.csv` (one row per entry, with the
  verdict for the 998 entries checked), `summary.json`, `summary.md` and `hand-checks.md` (all 17 stale copies).
- `tools/world_expiry.py`: the census (standard library only); `tools/test_world_expiry.py`: tests on made-up zips
  served from memory, with every expected value worked by hand. `tools/world_diff.py` and
  `tools/test_world_diff.py`: the comparison of two censuses. `tools/mirror_check.py` and
  `tools/test_mirror_check.py`: the mirror check, tested on made-up zips and API answers. `tools/source_check.py` and
  `tools/test_source_check.py`: the comparison with producers' files. `tools/stall_check.py` and
  `tools/test_stall_check.py`: the follow-up of stale copies and stalled downloads between two source checks. Tools
  are committed only after their tests pass.

## Reproduce

```
python tools/test_world_expiry.py -v
python tools/test_world_diff.py -v
python tools/test_mirror_check.py -v
python tools/test_source_check.py -v
python tools/test_stall_check.py -v
curl -o feeds_v2.csv https://files.mobilitydatabase.org/feeds_v2.csv
python tools/world_expiry.py --catalog feeds_v2.csv --statuses active,inactive,future --predictions X --out out/world
python tools/world_diff.py --before world/2026-10-22-all/feeds.csv --after out/world --predictions Y --out out/diff
python tools/mirror_check.py --catalog feeds_v2.csv --pause 1.0 --out out/mirror
python tools/source_check.py --catalog feeds_v2.csv --control 300 --seed 20261024 --out out/source
```

Census results go to `<out>/<as-of>/`: `feeds.csv` (one row per feed, with its catalog status), `by_country.csv`,
`summary.json` and `summary.md`. The mirror check writes `mirror.csv` (one row per `jbda-` entry), `missing.csv`
(repository feeds with no entry), `summary.json` and `summary.md`. The source check writes `sources.csv` (one row per
entry read), `summary.json` and `summary.md`. The catalog changes daily, so a later run gives different counts.

Source data: the Mobility Database by MobilityData (catalog metadata CC0 1.0) and the GTFS Data Repository API v2
(https://gtfs-data.jp/). Each dataset belongs to its publisher.
