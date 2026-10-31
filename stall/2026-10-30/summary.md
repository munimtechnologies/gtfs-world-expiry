# Stale copies and stalled downloads (2026-10-30)

A follow-up of the source check: are the earlier stale copies still stale, and how many entries whose copy still runs have a stalled download? A download is stalled when the producer serves a different file that still runs, whose Last-Modified day is after the day the catalog stored its copy and at least 3 days before the as-of date.

- earlier stale copies: 17; still_stale 16, no_new_copy_other 1, renewed 0, gone 0
- entries whose copy still runs and whose producer file was read: 2476; stalled downloads: 2; days the producer file had been up: n 2, median 34.5 days, quartiles 29.75–39.25, range 25–44
- stalled downloads by country: US 1, ES 1
- copy stored 2026-04-19 to 2026-06-18: stalled 1 of 2, other live entries read 145 of 2474
- stale copies in this run: 17, of which 1 were not stale in the earlier check

## 事前に記録した予測 / Predictions fixed before the run

- T1: Of the earlier stale copies that are still in the catalog with a readable copy, at least 70% have no new copy in the later run: the catalog has stored no newer file (the copy's Last-Modified day and last service day are both unchanged). Result: 100.0%, held.
- T2: Of the entries whose copy still runs and whose producer file is read with service dates, between 0.1% and 2.0% have a stalled download. Result: 0.1%, did not hold.
- T3: Predictions S2, S3 and S4 of the source check hold again in the later run. Result: S2 held, S3 held, S4 held, held.
- T4: Among the entries with a stalled download, the catalog stored the copy between 2026-04-19 and 2026-06-18 more often than among the other entries whose copy still runs and whose producer file is read (one-sided Fisher exact p < 0.05; not tested with fewer than 5 stalled downloads). Result: none, not tested.

## Entries

| id | kind | fate | country | provider | copy stored before | copy stored | copy's last day | producer Last-Modified | producer's last day | days waiting |
|---|---|---|---|---|---|---|---|---|---|---|
| mdb-1017 | stale_before | still_stale | ES | Metro de Málaga | 2026-05-13 | 2026-05-13 | 2026-07-07 | 2026-10-07 | 2026-11-19 |  |
| mdb-1053 | stale_before | still_stale | US | Loudoun County Transit | 2026-04-21 | 2026-04-21 | 2026-09-26 |  | 2027-03-27 |  |
| mdb-1189 | stale_before | still_stale | US | Blacksburg Transit | 2026-05-10 | 2026-05-10 | 2026-07-31 | 2026-10-05 | 2026-12-30 |  |
| mdb-1290 | stale_before | no_new_copy_other | PL | PKP Szybka Kolej Miejska (SKM) | 2026-06-18 | 2026-06-18 | 2026-08-29 |  |  |  |
| mdb-1304 | stale_before | still_stale | US | Kitsap Transit | 2026-05-20 | 2026-05-20 | 2026-09-12 | 2026-09-10 | 2026-12-05 |  |
| mdb-148 | stale_before | still_stale | US | Sun Metro | 2026-05-28 | 2026-05-28 | 2026-06-13 | 2026-10-12 | 2027-01-30 |  |
| mdb-190 | stale_before | still_stale | US | Metro St. Louis | 2026-05-29 | 2026-05-29 | 2026-06-14 | 2026-10-31 | 2026-11-29 |  |
| mdb-1903 | stale_before | still_stale | HU | V-BUSZ KFT | 2026-06-04 | 2026-06-04 | 2026-08-31 | 2026-09-29 | 2026-10-31 |  |
| mdb-2127 | stale_before | still_stale | US | Milwaukee County Transit System (MCTS) | 2025-05-08 | 2025-05-08 | 2025-08-23 | 2026-07-22 | 2026-12-05 |  |
| mdb-2610 | stale_before | still_stale | IT | AMT Genova | 2025-09-08 | 2025-09-08 | 2025-09-15 | 2026-10-25 | 2026-11-02 |  |
| mdb-368 | stale_before | still_stale | US | Metropolitan Atlanta Rapid Transit Authority (MART | 2026-04-19 | 2026-04-19 | 2026-08-21 | 2026-08-18 | 2026-12-11 |  |
| mdb-683 | stale_before | still_stale | AU | Department of Transport - Public Transport | 2024-09-02 | 2024-09-02 | 2025-01-30 |  | 2027-02-06 |  |
| mdb-866 | stale_before | still_stale | FI | Tampereen joukkoliikenne (JOLI) | 2026-05-13 | 2026-05-13 | 2026-08-04 | 2026-10-23 | 2027-06-06 |  |
| mdb-887 | stale_before | still_stale | HU | Szegedi Közlekedési Társaság | 2026-07-08 | 2026-07-08 | 2026-10-05 |  | 2026-12-31 |  |
| tdg-79499 | stale_before | still_stale | FR | Communauté d'Agglomération Royan Atlantique | 2026-03-11 | 2026-03-11 | 2026-07-07 | 2026-08-24 | 2027-07-06 |  |
| tld-4135 | stale_before | still_stale | US | High Point Transit | 2025-08-26 | 2025-08-26 | 2026-06-30 |  | 2026-12-31 |  |
| tld-7921 | stale_before | still_stale | CA | Hinton Transit | 2025-03-03 | 2025-03-03 | 2022-01-01 |  | 2030-01-01 |  |
| ntd-60118 | stale_new |  | US | City of Edmond |  | 2024-12-09 | 2025-12-31 |  | 2027-12-31 |  |
| mdb-96 | stalled_live |  | US | Metrolink |  | 2026-05-23 | 2027-12-31 | 2026-10-05 | 2027-12-31 | 25 |
| tld-767 | stalled_live |  | ES | Guaguas Municipales |  | 2025-12-18 | 2035-01-30 | 2026-09-16 | 2035-01-30 | 44 |

Limits: each producer URL is read once, from one place, and the catalog's fetcher may be served differently. Last-Modified headers are taken as given; a producer that sends none is never counted as stalled. Counts are per catalog entry, not per agency.

Generated 2026-10-31T07:44:56Z. Source: the Mobility Database catalog (feeds_v2.csv, CC0) and each producer's published file. Made by MV2 of Munim, Inc. with AI agents working in MV2's name. Data CC BY 4.0.
