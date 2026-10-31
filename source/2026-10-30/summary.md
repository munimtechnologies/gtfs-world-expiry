# The catalog's copy against the producer's own file (2026-10-30)

For GTFS feeds in the Mobility Database catalog (statuses active, inactive, future), the copy of the latest dataset the catalog serves (urls.latest) was compared with the file at the producer's own download URL (urls.direct_download). Every entry whose copy has no service left on the as-of date was checked (expired group, 701), and a seeded random sample of 2809 entries whose copy still has service (control group; seed 20261024). Two files are the same when they hold the same .txt members with the same CRC-32 and size. A stale copy is one whose producer serves a different file that still has service.

- catalog entries read: 3619 (active 2877, inactive 717, future 25)
- copies: ok 3547, no_latest 67, bad_zip 5
- expired group (701): same_file 463, differs_running 17, differs_ended 1, producer_no_dates 0, producer_unreadable 196, auth_required 24, no_direct_url 0
  - status active (23): same_file 10, differs_running 0, differs_ended 0, producer_no_dates 0, producer_unreadable 13, auth_required 0, no_direct_url 0
  - status inactive (678): same_file 453, differs_running 17, differs_ended 1, producer_no_dates 0, producer_unreadable 183, auth_required 24, no_direct_url 0
- control group (2809): same_file 2296, differs_running 180, differs_ended 0, producer_no_dates 0, producer_unreadable 172, auth_required 161, no_direct_url 0
- producer URLs that could not be read, expired group: http_404 107, network_error 30, bad_zip 20, http_403 15, http_416 10, http_501 4, http_301 3, bad_content_range 2, http_502 1, http_511 1, http_503 1, http_500 1, http_401 1
- producer URLs that could not be read, control group: http_404 78, network_error 24, bad_zip 19, http_416 19, http_501 14, http_403 10, too_big 6, http_301 1, http_429 1
- expired-group entries the catalog redirects to another entry: 4
- stale copies: 17; days since the copy ran out: n 17, median 115 days, quartiles 70.0–303.0, range 25–1763; producer file runs later by: n 17, median 184 days, quartiles 135.0–413.0, range 61–2922; producer Last-Modified before the as-of date: n 11, median 25 days, quartiles 12.5–58.5, range -1–100

## By catalog source (id prefix), expired group

- jbda (43): same_file 14, differs_running 0, differs_ended 0, producer_no_dates 0, producer_unreadable 29, auth_required 0, no_direct_url 0
- mdb (455): same_file 303, differs_running 13, differs_ended 0, producer_no_dates 0, producer_unreadable 115, auth_required 24, no_direct_url 0
- ntd (60): same_file 46, differs_running 1, differs_ended 0, producer_no_dates 0, producer_unreadable 13, auth_required 0, no_direct_url 0
- odpt (4): same_file 3, differs_running 0, differs_ended 0, producer_no_dates 0, producer_unreadable 1, auth_required 0, no_direct_url 0
- tdg (54): same_file 49, differs_running 1, differs_ended 0, producer_no_dates 0, producer_unreadable 4, auth_required 0, no_direct_url 0
- tld (85): same_file 48, differs_running 2, differs_ended 1, producer_no_dates 0, producer_unreadable 34, auth_required 0, no_direct_url 0

## 事前に記録した予測 / Predictions fixed before the run

- S1: Of the expired-group entries whose producer URL needs no key, between 35% and 85% return a readable zip with service dates. Result: 71.0%, held.
- S2: Of the expired-group entries whose producer file is read with service dates, at most 15% are stale copies: the producer's file differs from the catalog's copy and still has service on the as-of date. Result: 3.5%, held.
- S3: Of the expired-group entries whose producer file is read with service dates and has no service left either, at least 80% hold the same file as the catalog's copy. Result: 99.8%, held.
- S4: Of the control-group entries whose producer file is read with service dates, at least 80% hold the same file as the catalog's copy. Result: 92.7%, held.
- S5: Among the expired-group producer URLs that need no key and cannot be read, HTTP 404 is the most common result (strictly more often than any other). Result: http_404 107 of 196, held.

## Stale copies (expired group)

| id | status | country | provider | copy's last day | producer's last day | producer Last-Modified | days since copy ended |
|---|---|---|---|---|---|---|---|
| mdb-1017 | inactive | ES | Metro de Málaga | 2026-07-07 | 2026-11-19 | 2026-10-07 | 115 |
| mdb-1053 | inactive | US | Loudoun County Transit | 2026-09-26 | 2027-03-27 |  | 34 |
| mdb-1189 | inactive | US | Blacksburg Transit | 2026-07-31 | 2026-12-30 | 2026-10-05 | 91 |
| mdb-1304 | inactive | US | Kitsap Transit | 2026-09-12 | 2026-12-05 | 2026-09-10 | 48 |
| mdb-148 | inactive | US | Sun Metro | 2026-06-13 | 2027-01-30 | 2026-10-12 | 139 |
| mdb-190 | inactive | US | Metro St. Louis | 2026-06-14 | 2026-11-29 | 2026-10-31 | 138 |
| mdb-1903 | inactive | HU | V-BUSZ KFT | 2026-08-31 | 2026-10-31 | 2026-09-29 | 60 |
| mdb-2127 | inactive | US | Milwaukee County Transit System (MCTS) | 2025-08-23 | 2026-12-05 | 2026-07-22 | 433 |
| mdb-2610 | inactive | IT | AMT Genova | 2025-09-15 | 2026-11-02 | 2026-10-25 | 410 |
| mdb-368 | inactive | US | Metropolitan Atlanta Rapid Transit Authority (MARTA) | 2026-08-21 | 2026-12-11 | 2026-08-18 | 70 |
| mdb-683 | inactive | AU | Department of Transport - Public Transport | 2025-01-30 | 2027-02-06 |  | 638 |
| mdb-866 | inactive | FI | Tampereen joukkoliikenne (JOLI) | 2026-08-04 | 2027-06-06 | 2026-10-23 | 87 |
| mdb-887 | inactive | HU | Szegedi Közlekedési Társaság | 2026-10-05 | 2026-12-31 |  | 25 |
| ntd-60118 | inactive | US | City of Edmond | 2025-12-31 | 2027-12-31 |  | 303 |
| tdg-79499 | inactive | FR | Communauté d'Agglomération Royan Atlantique | 2026-07-07 | 2027-07-06 | 2026-08-24 | 115 |
| tld-4135 | inactive | US | High Point Transit | 2026-06-30 | 2026-12-31 |  | 122 |
| tld-7921 | inactive | CA | Hinton Transit | 2022-01-01 | 2030-01-01 |  | 1763 |

Limits: each file is read once, on one day; a producer that published a new file that day can show as a difference the catalog would pick up at its next daily check. A producer URL can serve a different file to the catalog's fetcher (blocking, geography, a changed URL the catalog has not recorded). Last-Modified headers are taken as given. Files that differ only in feed_info or other members count as different. Service dates come from the calendar files only. Counts are per catalog entry, not per agency, and a few files are catalogued twice.

Generated 2026-10-31T07:44:55Z. Source: the Mobility Database catalog (feeds_v2.csv, CC0) and each producer's published file. Feed contents stay under their publishers' licences and are not redistributed. Made by MV2 of Munim, Inc. with AI agents working in MV2's name. Data CC BY 4.0.
