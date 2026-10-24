# The catalog's copy against the producer's own file (2026-10-23)

For GTFS feeds in the Mobility Database catalog (statuses active, inactive, future), the copy of the latest dataset the catalog serves (urls.latest) was compared with the file at the producer's own download URL (urls.direct_download). Every entry whose copy has no service left on the as-of date was checked (expired group, 698), and a seeded random sample of 300 entries whose copy still has service (control group; seed 20261024). Two files are the same when they hold the same .txt members with the same CRC-32 and size. A stale copy is one whose producer serves a different file that still has service.

- catalog entries read: 3615 (active 2880, inactive 721, future 14)
- copies: ok 3541, no_latest 69, bad_zip 5
- expired group (698): same_file 461, differs_running 17, differs_ended 1, producer_no_dates 0, producer_unreadable 196, auth_required 23, no_direct_url 0
  - status active (25): same_file 11, differs_running 0, differs_ended 0, producer_no_dates 0, producer_unreadable 14, auth_required 0, no_direct_url 0
  - status inactive (673): same_file 450, differs_running 17, differs_ended 1, producer_no_dates 0, producer_unreadable 182, auth_required 23, no_direct_url 0
- control group (300): same_file 239, differs_running 8, differs_ended 0, producer_no_dates 0, producer_unreadable 32, auth_required 21, no_direct_url 0
- producer URLs that could not be read, expired group: http_404 105, network_error 30, bad_zip 20, http_403 16, http_416 10, http_501 4, http_301 3, bad_content_range 2, http_502 2, http_500 2, http_511 1, http_401 1
- producer URLs that could not be read, control group: http_404 11, http_502 7, network_error 3, bad_zip 3, http_501 3, http_416 3, http_403 2
- expired-group entries the catalog redirects to another entry: 4
- stale copies: 17; days since the copy ran out: n 17, median 108 days, quartiles 55.0–132.0, range 18–1756; producer file runs later by: n 17, median 182 days, quartiles 112.0–364.0, range 61–2922; producer Last-Modified before the as-of date: n 12, median 17.0 days, quartiles 3.75–47.25, range -1–93

## By catalog source (id prefix), expired group

- jbda (43): same_file 14, differs_running 0, differs_ended 0, producer_no_dates 0, producer_unreadable 29, auth_required 0, no_direct_url 0
- mdb (451): same_file 299, differs_running 14, differs_ended 0, producer_no_dates 0, producer_unreadable 115, auth_required 23, no_direct_url 0
- ntd (60): same_file 48, differs_running 0, differs_ended 0, producer_no_dates 0, producer_unreadable 12, auth_required 0, no_direct_url 0
- odpt (4): same_file 3, differs_running 0, differs_ended 0, producer_no_dates 0, producer_unreadable 1, auth_required 0, no_direct_url 0
- tdg (54): same_file 48, differs_running 1, differs_ended 0, producer_no_dates 0, producer_unreadable 5, auth_required 0, no_direct_url 0
- tld (86): same_file 49, differs_running 2, differs_ended 1, producer_no_dates 0, producer_unreadable 34, auth_required 0, no_direct_url 0

## 事前に記録した予測 / Predictions fixed before the run

- S1: Of the expired-group entries whose producer URL needs no key, between 35% and 85% return a readable zip with service dates. Result: 71.0%, held.
- S2: Of the expired-group entries whose producer file is read with service dates, at most 15% are stale copies: the producer's file differs from the catalog's copy and still has service on the as-of date. Result: 3.5%, held.
- S3: Of the expired-group entries whose producer file is read with service dates and has no service left either, at least 80% hold the same file as the catalog's copy. Result: 99.8%, held.
- S4: Of the control-group entries whose producer file is read with service dates, at least 80% hold the same file as the catalog's copy. Result: 96.8%, held.
- S5: Among the expired-group producer URLs that need no key and cannot be read, HTTP 404 is the most common result (strictly more often than any other). Result: http_404 105 of 196, held.

## Stale copies (expired group)

| id | status | country | provider | copy's last day | producer's last day | producer Last-Modified | days since copy ended |
|---|---|---|---|---|---|---|---|
| mdb-1017 | inactive | ES | Metro de Málaga | 2026-07-07 | 2026-11-19 | 2026-10-07 | 108 |
| mdb-1053 | inactive | US | Loudoun County Transit | 2026-09-26 | 2027-03-27 |  | 27 |
| mdb-1189 | inactive | US | Blacksburg Transit | 2026-07-31 | 2026-12-30 | 2026-10-05 | 84 |
| mdb-1290 | inactive | PL | PKP Szybka Kolej Miejska (SKM) | 2026-08-29 | 2026-12-12 | 2026-10-23 | 55 |
| mdb-1304 | inactive | US | Kitsap Transit | 2026-09-12 | 2026-12-05 | 2026-09-10 | 41 |
| mdb-148 | inactive | US | Sun Metro | 2026-06-13 | 2027-01-30 | 2026-10-12 | 132 |
| mdb-190 | inactive | US | Metro St. Louis | 2026-06-14 | 2026-11-29 | 2026-10-24 | 131 |
| mdb-1903 | inactive | HU | V-BUSZ KFT | 2026-08-31 | 2026-10-31 | 2026-09-29 | 53 |
| mdb-2127 | inactive | US | Milwaukee County Transit System (MCTS) | 2025-08-23 | 2026-12-05 | 2026-07-22 | 426 |
| mdb-2610 | inactive | IT | AMT Genova | 2025-09-15 | 2026-10-26 | 2026-10-18 | 403 |
| mdb-368 | inactive | US | Metropolitan Atlanta Rapid Transit Authority (MARTA) | 2026-08-21 | 2026-12-11 | 2026-08-18 | 63 |
| mdb-683 | inactive | AU | Department of Transport - Public Transport | 2025-01-30 | 2027-02-06 |  | 631 |
| mdb-866 | inactive | FI | Tampereen joukkoliikenne (JOLI) | 2026-08-04 | 2027-06-06 | 2026-10-23 | 80 |
| mdb-887 | inactive | HU | Szegedi Közlekedési Társaság | 2026-10-05 | 2026-12-31 |  | 18 |
| tdg-79499 | inactive | FR | Communauté d'Agglomération Royan Atlantique | 2026-07-07 | 2027-07-06 | 2026-08-24 | 108 |
| tld-4135 | inactive | US | High Point Transit | 2026-06-30 | 2026-12-31 |  | 115 |
| tld-7921 | inactive | CA | Hinton Transit | 2022-01-01 | 2030-01-01 |  | 1756 |

Limits: each file is read once, on one day; a producer that published a new file that day can show as a difference the catalog would pick up at its next daily check. A producer URL can serve a different file to the catalog's fetcher (blocking, geography, a changed URL the catalog has not recorded). Last-Modified headers are taken as given. Files that differ only in feed_info or other members count as different. Service dates come from the calendar files only. Counts are per catalog entry, not per agency, and a few files are catalogued twice.

Generated 2026-10-24T05:13:42Z. Source: the Mobility Database catalog (feeds_v2.csv, CC0) and each producer's published file. Feed contents stay under their publishers' licences and are not redistributed. Made by MV2 of Munim, Inc. with AI agents working in MV2's name. Data CC BY 4.0.
