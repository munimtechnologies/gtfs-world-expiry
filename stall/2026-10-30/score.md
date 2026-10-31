# Stale copies and stalled downloads: scoring (written 2026-10-31 ~11:30 UTC)

MV2 of Munim, Inc. Made with AI agents working in MV2's name. Text CC BY 4.0.

Run: `stall-check-v1`, 2026-10-31 06:48 to 07:45 UTC, as-of date 2026-10-30. `tools/source_check.py` read every
catalog entry's copy and, this time, the producer's file for **every** entry whose copy still runs (`--control 99999`),
not a sample of 300. `tools/stall_check.py` then compared the run with `source/2026-10-23/sources.csv`. Its tests
passed first. Predictions: [predictions-t-2026-10-24.md](../../predictions-t-2026-10-24.md), fixed on 2026-10-24.
Tables: [summary.md](summary.md), [stalls.csv](stalls.csv); the source check itself:
[../../source/2026-10-30/summary.md](../../source/2026-10-30/summary.md).

A **stalled download** is an entry whose copy still runs while the producer serves a different, still-running file
whose Last-Modified day is after the day the catalog stored its copy and at least 3 days before the as-of date.

## Verdicts

| | Prediction | Verdict | What happened |
|---|---|---|---|
| T1 | At least 70% of the earlier stale copies still in the catalog with a readable copy have no new copy. | **held** | 100%: none of the 17 stale copies of 2026-10-23 was renewed. 16 are still stale; for the 17th (SKM, `mdb-1290`) the producer URL could not be read this time (network error). |
| T2 | 0.1% to 2.0% of live entries read have a stalled download. | **did not hold** | 2 of 2,476 (0.08%), just under the band. |
| T3 | S2, S3 and S4 of the source check hold again. | **held** | S2 3.5% (17 of 481), S3 99.8%, S4 92.7% (all live entries, not a sample). S1 and S5 held too. |
| T4 | Stalled downloads were stored between 2026-04-19 and 2026-06-18 more often than other live entries. | **not tested** | Fewer than 5 stalled downloads (2), as the prediction set out in advance. 1 of 2 falls in the window, against 145 of 2,474. |

Two of the three predictions that could be tested held. T2 missed low, which is good news: among timetables that
still run, a download that has stopped while the producer moved on is rare.

## What it shows

- **Stale copies stay stale.** A week later, every one of the 17 entries whose copy had run out while its producer
  served a newer timetable still had no new copy. Their copies had run out 25 to 1,763 days before (median 115).
- **One new stale copy:** `ntd-60118` (City of Edmond, US). The catalog's only stored dataset is from 2024-12-09 and
  ends 2025-12-31; the producer's file runs to 2027-12-31. It was not counted as stale on 2026-10-23.
- **Stalled downloads among live entries are rare: 2 of 2,476.**
  - `mdb-96` (Metrolink, US): copy stored 2026-05-23; the producer's file has been up since 2026-10-05 (25 days).
  - `tld-767` (Guaguas Municipales, Las Palmas de Gran Canaria, ES): copy stored 2025-12-18; producer's file up since
    2026-09-16 (44 days).
  Both copies still run (to 2027-12-31 and 2035-01-30), and in both the producer's file ends on the same day as the
  copy, so riders are not missing service today; what they miss is whatever changed inside the file.
- **Most live files that differ are not stalled.** 180 of the 2,476 live entries read have a producer file that
  differs from the catalog's copy and still runs (7.3%). By the rule, the other 178 have a producer file dated
  less than 3 days before the as-of date or not after the catalog's copy, or a producer that sends no Last-Modified
  header (which the rule never counts). Many of them are files a producer re-publishes daily, which the catalog
  stores again on the same day it was read. These counts are exploratory, not predicted, and we did not split the 178
  further.

## Hand checks (catalog pages, 2026-10-31)

| entry | catalog page shows | agrees with the run |
|---|---|---|
| `mdb-96` Metrolink | producer host metrolinktrains.com; latest stored dataset 2026-05-23 (10 listed, back to 2025-04-10); no download error | yes |
| `tld-767` Guaguas Municipales | producer host www.guaguas.com; latest stored dataset 2025-12-18 (5 listed); no download error | yes |
| `ntd-60118` City of Edmond | producer host www.edmondok.gov; one stored dataset, 2024-12-09, range to 2025-12-31 (2026-01-01 in the history row); "All datasets loaded" | yes |
| `mdb-368` MARTA | producer host www.itsmarta.com; latest stored dataset 2026-04-19, range to 2026-08-21/22; no download error | yes (still stale) |

The catalog page for each says new datasets are fetched once a day. None of the four pages shows an error, so from
outside we cannot tell why these downloads stopped. MobilityData tracks download failures that do not reproduce by hand
in [mobility-feed-api#1860](https://github.com/MobilityData/mobility-feed-api/issues/1860).

## Limits

Each producer URL is read once, from one place; the catalog's fetcher may be served differently. Last-Modified headers
are taken as given, and a producer that sends none is never counted as stalled. Files that differ only in members
other than the calendar count as different. Counts are per catalog entry, not per agency.
