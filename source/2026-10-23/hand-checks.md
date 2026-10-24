# Source check 2026-10-23: hand checks and exploratory counts

Checked on 2026-10-24 (UTC), after the job had finished and before anything was published. By MV2 of Munim, Inc.;
made with AI agents working in MV2's name. Text CC BY 4.0.

## Totals re-added from summary.json

- Expired group: 461 + 17 + 1 + 0 + 196 + 23 + 0 = 698, the size of the group.
- Control group: 239 + 8 + 0 + 0 + 32 + 21 + 0 = 300, the size of the sample.
- S1: 479 read of 675 with no key (698 minus 23 needing a key) = 71.0%. S2: 17 of 479 = 3.5%. S3: 461 of 462
  (479 minus the 17 stale copies) = 99.8%. S4: 239 of 247 = 96.8%. S5: the twelve failure counts add to 196, and
  HTTP 404 (105) is the largest.
- The 43 `jbda-` entries in the expired group split 14 same file and 29 unreadable, as the mirror check of the same
  day found by a different route (14 hold the repository's current file, 29 have none).

## Six stale copies checked on their catalog pages

For each entry, the catalog page (`https://mobilitydatabase.org/feeds/gtfs/<id>`) was read on 2026-10-24. In all
six, the producer URL on the page is the `urls.direct_download` the tool read, the latest download on the page is the
day the tool recorded for the catalog's copy (`mirror_modified`), and the page shows no download error.

| id | provider | catalog's latest download | its service ends | producer's file (read 2026-10-24) | earlier downloads on the page |
|---|---|---|---|---|---|
| mdb-368 | MARTA (Atlanta, US) | 2026-04-19 | 2026-08-21 | runs to 2026-12-11, Last-Modified 2026-08-18 | every 1-3 months from May 2025 to Apr 2026 |
| mdb-866 | Tampere (JOLI, FI) | 2026-05-13 | 2026-08-04 | runs to 2027-06-06, Last-Modified 2026-10-23 | every 1-4 weeks from Jan 2026 to 2026-05-13 |
| mdb-1017 | Metro de Málaga (ES) | 2026-05-13 | 2026-07-07 | runs to 2026-11-19, Last-Modified 2026-10-07 | every 1-2 months until 2026-05-13 |
| mdb-190 | Metro St. Louis (US) | 2026-05-29 | 2026-06-14 | runs to 2026-11-29, Last-Modified 2026-10-24 | weekly from 2026-03-24 to 2026-05-29 |
| mdb-2127 | Milwaukee County Transit System (US) | 2025-05-08 | 2025-08-23 | runs to 2026-12-05, Last-Modified 2026-07-22 | every few months from Oct 2024 to 2025-05-08 |
| tdg-79499 | Cara'bus, Royan Atlantique (FR) | 2026-03-11 | 2026-07-07 | runs to 2027-07-06, Last-Modified 2026-08-24 | 2025-12-10 |

The catalog's FAQ says it checks producer URLs once a day. A producer that was downloaded every week until a given
day and then never again, while its URL now serves a newer timetable, points to downloads that stopped working for
that entry, not to a producer that stopped publishing. We do not know why they stopped: the catalog's fetcher may be
answered differently from ours (MobilityData's own issue
[mobility-feed-api#1860](https://github.com/MobilityData/mobility-feed-api/issues/1860), opened 2026-10-08, describes a
feed that fails every night but downloads fine by hand), or something else may be wrong.

Already known to MobilityData (searched 2026-10-24): Málaga (`mdb-1017`) has an open catalog issue,
[mobility-database-catalogs#1618](https://github.com/MobilityData/mobility-database-catalogs/issues/1618), asking to
move it to Spain's national access point, with a 2026-10-14 comment that a User-Agent problem is involved. AMT Genova
(`mdb-2610`) has an open automated update submission with the same URL
([#1684](https://github.com/MobilityData/mobility-database-catalogs/issues/1684)). A search of the catalogs repository for
the ids and names of MARTA, Tampere, Milwaukee, Kitsap, Blacksburg, Metro St. Louis, Sun Metro, Loudoun, Szeged and
Hinton found no issue about their downloads.

## Exploratory counts (not predicted)

These were found after the run and get no claim beyond what they are.

- Producer files that had been up for days: 12 of the 17 producer URLs send a Last-Modified header. In 9 of them it is
  5 to 93 days before the as-of date (Málaga, Blacksburg, Kitsap, Sun Metro, V-BUSZ, Milwaukee, AMT Genova, MARTA,
  Royan), so a daily check should already have seen the new file. In the other 3 (SKM, Metro St. Louis, Tampere) the
  current file is 0 or 1 day old; the catalog pages of Metro St. Louis and Tampere show downloads every one to four
  weeks until May 2026 and none since.
- When the catalog's copies were stored: 10 of the 17 stale copies were stored between 2026-04-19 and 2026-06-18
  (Loudoun, MARTA, Blacksburg, Málaga, Tampere, Kitsap, Sun Metro, Metro St. Louis, V-BUSZ, SKM). Among the 461
  expired entries whose producer serves the same file, 16 were stored in that window. Many downloads that last worked
  in the same two months suggest a common cause, but this is a pattern, not a finding about the cause.
- The 8 control-group entries whose producer file differs are not stale: in all 8 the catalog's copy still runs, and
  the producer's file runs at most 9 days longer. In all 8 the catalog stored its copy between 2026-10-22 and
  2026-10-24, so the difference is a file published around the time of the run.

## Limits

Each producer URL was read once, from one place. The catalog's fetcher may be served differently. Six of the 17 stale
copies were checked by hand; the other 11 rest on the tool's reading only. Last-Modified headers are taken as given.
