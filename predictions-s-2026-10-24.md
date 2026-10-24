# Predictions S1–S5: the catalog's copy against the producer's own file (fixed 2026-10-24)

By MV2 of Munim, Inc. Made with AI agents working in MV2's name. Text CC BY 4.0.

These predictions were written and published before any producer file was read for this check. They are scored by
`tools/source_check.py`, which writes them into its `summary.json` and `summary.md`.

## The question

The Mobility Database serves its own copy of each feed's latest dataset (`urls.latest`) and records where the
producer publishes it (`urls.direct_download`). Its FAQ says producer URLs are checked for updates every day. Our
second census found 698 of 3,502 catalogued GTFS feeds whose copy has no service left. Does that mean the producer
has stopped publishing a valid timetable, or does the producer serve a newer file the catalog has not picked up (a
stale copy)?

## Method (fixed in advance)

- Catalog: `feeds_v2.csv` on the day of the run; GTFS Schedule rows with status `active`, `inactive` or `future`.
- Every copy is read (calendar files only, through range requests). The **expired group** is every entry whose copy
  is read and whose last service date is before the as-of date (one day before the UTC run date). The **control
  group** is a seeded random sample (seed 20261024) of 300 entries whose copy still has service.
- For both groups the producer's URL is read the same way, unless the catalog says it needs a key (then it is not
  read). Two files are the same when they hold the same `.txt` members with the same CRC-32 and size.
- Verdicts: `same_file`; `differs_running` (a different file that still has service on the as-of date: for the
  expired group, a **stale copy**); `differs_ended` (a different file that has also ended); `producer_no_dates`;
  `producer_unreadable` (HTTP error, network error, not a zip, too big); `auth_required`; `no_direct_url`.

## Predictions

| | Prediction |
|---|---|
| S1 | Of the expired-group entries whose producer URL needs no key, between 35% and 85% return a readable zip with service dates. |
| S2 | Of the expired-group entries whose producer file is read with service dates, at most 15% are stale copies (`differs_running`). |
| S3 | Of the expired-group entries whose producer file is read with service dates and has no service left either, at least 80% hold the same file as the catalog's copy. |
| S4 | Of the control-group entries whose producer file is read with service dates, at least 80% hold the same file as the catalog's copy. |
| S5 | Among the expired-group producer URLs that need no key and cannot be read, HTTP 404 is the most common result (strictly more often than any other). |

## What we knew when writing them

- Our mirror check of Japan's GTFS Data Repository (`mirror/2026-10-24/`) found **no** stale copy among the 43
  `jbda-` entries whose copy had ended: 29 had no current file at the repository any more (mostly HTTP 404), and 14
  held exactly the repository's current file, whose own calendar had also ended. (Our first write-up of that check
  wrongly called 13 of them stale; see the README's correction.) That is one national source with one URL scheme, so
  S2 allows up to 15% worldwide.
- ITS Feed's September 2026 check of 828 US catalog entries not marked inactive found that 92 producer URLs did not
  return a zip, 38 of them with HTTP 404, the most common failure. Expired and inactive entries were not checked
  there; S1 and S5 extend that picture to them.
- Producers that rebuild their zip every day (new `feed_info` or a regenerated file) would show as different files
  without any real change; S4 allows for that.

## Limits stated in advance

One reading on one day. A producer can serve its URL differently to the catalog's fetcher than to ours. Files that
differ only in non-calendar members count as different. Counts are per catalog entry.
