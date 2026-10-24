# Predictions T1–T4: stale copies and stalled downloads (fixed 2026-10-24)

By MV2 of Munim, Inc. Made with AI agents working in MV2's name. Text CC BY 4.0.

These predictions were written on 2026-10-24, after the source check of 2026-10-23 (`source/2026-10-23/`) and before
the follow-up run they score. That run will be made on or after 2026-10-30 with `tools/source_check.py --control
99999`, so that every catalog entry whose copy still runs is compared with its producer's file, not a sample. It is
then scored by `tools/stall_check.py` against `source/2026-10-23/sources.csv`.

## Definitions

- **Stale copy** (as in the source check): the catalog's copy has no service left on the as-of date, and the
  producer's own URL serves a different file that still has service.
- **New copy:** between the two runs, the catalog's copy got a later Last-Modified day or a different last service
  day.
- **Stalled download:** the catalog's copy still runs on the as-of date, and the producer serves a different file that
  still runs, whose Last-Modified day is after the day the catalog stored its copy and at least 3 days before the
  as-of date. A producer that sends no Last-Modified header is never counted as stalled.
- **Live entries read:** the catalog's copy still runs on the as-of date and the producer's file was read with
  service dates.

## Predictions

| | Prediction |
|---|---|
| T1 | Of the 17 stale copies of 2026-10-23 that are still in the catalog with a readable copy, at least 70% have no new copy in the follow-up run. |
| T2 | Of the live entries read, between 0.1% and 2.0% have a stalled download. |
| T3 | Predictions S2, S3 and S4 of the source check hold again in the follow-up run (S4 then covers every live entry, not a sample of 300). |
| T4 | Among entries with a stalled download, the catalog stored the copy between 2026-04-19 and 2026-06-18 more often than among the other live entries read (one-sided Fisher exact p < 0.05). Not tested with fewer than 5 stalled downloads. |

## Why these numbers

- T1: the six stale copies checked by hand had gone 5 to 18 months without a new download, and the catalog's own work
  on download failures (mobility-feed-api#1860) was still open on 2026-10-24. A week is short, so most should stay
  stale. If MobilityData fixes the cause in that week, T1 misses, and that is good news.
- T2: the control sample of 2026-10-23 had 0 stalled downloads among 247 live entries read (8 differing files, all
  stored by the catalog within a day of the run). That puts the rate under about 1.2%, but the catalog-wide stall
  seen in expired entries (17 of 479) should also hit some entries whose copy still runs; Avon Transit
  (`mdb-2433`), whose copy dates from 2026-05-14 and for which MobilityData added a download header on 2026-10-15, may
  be one. So the range says stalls exist among live entries but are rare.
- T3: S2 to S4 were loose and held with room (3.5%, 99.8%, 96.8%).
- T4: tests out of sample the pattern found after the first run (10 of 17 stale copies stored in those two months,
  against 16 of 461 same-file entries). The window is fixed here and is not moved.

## Not predicted

Anything else in the follow-up output (countries, hosts, the number of new stale copies) is exploratory and will be
labelled so.
