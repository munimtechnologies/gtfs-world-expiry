# Source check 2026-10-23: hand checks and exploratory counts

Checked on 2026-10-24 (UTC), after the job had finished. The first six catalog pages were read before the v0.4.0
release and the other eleven later the same day (v0.4.1). By MV2 of Munim, Inc.; made with AI agents working in
MV2's name. Text CC BY 4.0.

## Totals re-added from summary.json

- Expired group: 461 + 17 + 1 + 0 + 196 + 23 + 0 = 698, the size of the group.
- Control group: 239 + 8 + 0 + 0 + 32 + 21 + 0 = 300, the size of the sample.
- S1: 479 read of 675 with no key (698 minus 23 needing a key) = 71.0%. S2: 17 of 479 = 3.5%. S3: 461 of 462
  (479 minus the 17 stale copies) = 99.8%. S4: 239 of 247 = 96.8%. S5: the twelve failure counts add to 196, and
  HTTP 404 (105) is the largest.
- The 43 `jbda-` entries in the expired group split 14 same file and 29 unreadable, as the mirror check of the same
  day found by a different route (14 hold the repository's current file, 29 have none).

## All 17 stale copies checked on their catalog pages

For each entry, the catalog page (`https://mobilitydatabase.org/feeds/gtfs/<id>`) was read on 2026-10-24. In all
17, the producer URL on the page is on the host the tool read (`producer_host` in `sources.csv`), the latest stored
download on the page is the day the tool recorded for the catalog's copy (`mirror_modified`), and the page shows no
download error. The pages show at most the ten latest downloads. Where a page's summary and its history row give end
dates one day apart, the tool's reading (`mirror_last`) matches the summary.

| id | provider | catalog's latest download | its service ends | producer's file (read 2026-10-23/24) | earlier downloads on the page |
|---|---|---|---|---|---|
| mdb-368 | MARTA (Atlanta, US) | 2026-04-19 | 2026-08-21 | runs to 2026-12-11, Last-Modified 2026-08-18 | every 1-3 months from May 2025 to Apr 2026 |
| mdb-866 | Tampere (JOLI, FI) | 2026-05-13 | 2026-08-04 | runs to 2027-06-06, Last-Modified 2026-10-23 | every 1-4 weeks from Jan 2026 to 2026-05-13 |
| mdb-1017 | Metro de Málaga (ES) | 2026-05-13 | 2026-07-07 | runs to 2026-11-19, Last-Modified 2026-10-07 | every 1-2 months until 2026-05-13 |
| mdb-190 | Metro St. Louis (US) | 2026-05-29 | 2026-06-14 | runs to 2026-11-29, Last-Modified 2026-10-24 | weekly from 2026-03-24 to 2026-05-29 |
| mdb-2127 | Milwaukee County Transit System (US) | 2025-05-08 | 2025-08-23 | runs to 2026-12-05, Last-Modified 2026-07-22 | every few months from Oct 2024 to 2025-05-08 |
| tdg-79499 | Cara'bus, Royan Atlantique (FR) | 2026-03-11 | 2026-07-07 | runs to 2027-07-06, Last-Modified 2026-08-24 | 2025-12-10 |
| mdb-1053 | Loudoun County Transit (US) | 2026-04-21 | 2026-09-26 | runs to 2027-03-27, no Last-Modified | every 1-4 months from Jul 2024 to 2026-04-21 |
| mdb-1189 | Blacksburg Transit (US) | 2026-05-10 | 2026-07-31 | runs to 2026-12-30, Last-Modified 2026-10-05 | ten downloads from 2026-03-06 to 2026-05-10, all with the same service range |
| mdb-1290 | PKP SKM, Tricity rail (PL) | 2026-06-18 | 2026-08-29 | runs to 2026-12-12, Last-Modified 2026-10-23 | daily from 2026-06-09 to 2026-06-18 |
| mdb-1304 | Kitsap Transit (US) | 2026-05-20 | 2026-09-12 | runs to 2026-12-05, Last-Modified 2026-09-10 | every few days to 3 months from Sep 2025 to 2026-05-20 |
| mdb-148 | Sun Metro (El Paso, US) | 2026-05-28 | 2026-06-13 | runs to 2027-01-30, Last-Modified 2026-10-12 | from Oct 2024; in 2026 on 01-17, 04-10, 04-23 and 05-28 |
| mdb-1903 | V-BUSZ, Veszprém (HU) | 2026-06-04 | 2026-08-31 | runs to 2026-10-31, Last-Modified 2026-09-29 | every few days to 6 weeks from Sep 2025 to 2026-06-04 |
| mdb-2610 | AMT Genova (IT) | 2025-09-08 | 2025-09-15 | runs to 2026-10-26, Last-Modified 2026-10-18 | every Monday from 2025-06-09 to 2025-09-08 (gap 2025-06-23 to 07-21), each file with a one-week calendar |
| mdb-683 | Alice Springs bus network, NT (AU) | 2024-09-02 | 2025-01-30 | runs to 2027-02-06, no Last-Modified | 2024-08-01 only |
| mdb-887 | Szeged (SzKT, HU) | 2026-07-08 | 2026-10-05 | runs to 2026-12-31, no Last-Modified | every few days to 10 weeks from Dec 2025 to 2026-07-08 |
| tld-4135 | High Point Transit (US) | 2025-08-26 | 2026-06-30 | runs to 2026-12-31, no Last-Modified | 2024-12-06, 2024-12-16, 2025-02-13 |
| tld-7921 | Hinton Transit (CA) | 2025-03-03 | 2022-01-01 | runs to 2030-01-01, no Last-Modified | none: this is the only download listed |

The catalog's FAQ says it checks producer URLs once a day. The evidence that downloads stopped while the producer
kept publishing is not equally strong for all 17:

- **Newer file on the server for days (9):** Málaga, Blacksburg, Kitsap, Sun Metro, V-BUSZ, Milwaukee, AMT Genova,
  MARTA and Royan send a Last-Modified header 5 to 93 days before the as-of date, so a daily check should already have
  stored the newer file.
- **Frequent downloads that stop on one day (3):** SKM, Metro St. Louis and Tampere serve a file that is 0 or 1 day
  old, but their pages show downloads every day (SKM), every week (Metro St. Louis) or every one to four weeks
  (Tampere) until May or June 2026, and none since. A producer that republishes this often has almost certainly
  published since.
- **Stale, but when the newer file appeared is unknown (5):** Loudoun, Alice Springs, Szeged, High Point and Hinton
  send no Last-Modified header. Their copies are stale (the producer serves a different file that still runs), but the
  newer file could be recent. Hinton's only download, on 2025-03-03, was already a file whose calendar ended in 2022.

Blacksburg's ten listed downloads all carry the same service range, so the catalog stores a new dataset when the file
changes, not only when its dates do. A producer file that differs from the stored copy should therefore have been
stored at the next successful daily check.

We do not know why the downloads stopped. The catalog's fetcher may be answered differently from ours: MobilityData's
own issue [mobility-feed-api#1860](https://github.com/MobilityData/mobility-feed-api/issues/1860), opened 2026-10-08,
describes a feed that fails every night but downloads fine by hand.

## Earlier public reports (searched 2026-10-24)

- Málaga (`mdb-1017`): open catalog issue
  [mobility-database-catalogs#1618](https://github.com/MobilityData/mobility-database-catalogs/issues/1618), asking to
  move it to Spain's national access point, with a 2026-10-14 comment that a User-Agent problem is involved.
- AMT Genova (`mdb-2610`): open automated update submission with the same URL
  ([#1684](https://github.com/MobilityData/mobility-database-catalogs/issues/1684)). Its catalog page is labelled
  "Accessible to European users only"; the tool's read of the producer URL on 2026-10-23/24 returned a readable file.
- Alice Springs (`mdb-683`): named in
  [mobility-feed-api#502](https://github.com/MobilityData/mobility-feed-api/issues/502) (2024-06-19) as a URL that
  served an HTML page instead of the zip to scripted downloads. That issue was closed on 2024-07-03; the page lists two
  downloads after it (2024-08-01 and 2024-09-02) and none since.
- SKM (`mdb-1290`): [mobility-database-catalogs#957](https://github.com/MobilityData/mobility-database-catalogs/issues/957)
  (2025, closed) replaced an outdated feed with the URL the entry now uses. It is not about the current stall.
- A search of the catalogs repository for the ids and names of MARTA, Tampere, Milwaukee, Kitsap, Blacksburg, Metro
  St. Louis, Sun Metro, Loudoun, Szeged and Hinton, and of both repositories for SKM, V-BUSZ, High Point, Alice Springs
  and Royan, found no other issue about these downloads.

## Exploratory counts (not predicted)

These were found after the run and get no claim beyond what they are.

- Producer files that had been up for days: 12 of the 17 producer URLs send a Last-Modified header. In 9 of them it is
  5 to 93 days before the as-of date (listed above). In the other 3 (SKM, Metro St. Louis, Tampere) the current file is
  0 or 1 day old.
- When the catalog's copies were stored: 10 of the 17 stale copies were stored between 2026-04-19 and 2026-06-18
  (Loudoun, MARTA, Blacksburg, Málaga, Tampere, Kitsap, Sun Metro, Metro St. Louis, V-BUSZ, SKM), and an 11th
  (Szeged) on 2026-07-08. Among the 461 expired entries whose producer serves the same file, 16 were stored between
  2026-04-19 and 2026-06-18. Many downloads that last worked in the same few months suggest a common cause, but this is
  a pattern, not a finding about the cause. Prediction T4 tests it out of sample.
- The 8 control-group entries whose producer file differs are not stale: in all 8 the catalog's copy still runs, and
  the producer's file runs at most 9 days longer. In all 8 the catalog stored its copy between 2026-10-22 and
  2026-10-24, so the difference is a file published around the time of the run.

## Limits

Each producer URL was read once, from one place. The catalog's fetcher may be served differently. The hand checks
compare the producer's host, not the full URL, with the tool's reading, and read each catalog page once; the pages
list at most ten downloads. Last-Modified headers are taken as given.
