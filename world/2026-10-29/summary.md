# GTFS feeds with no service left, worldwide, as of 2026-10-29

Source: the Mobility Database catalog (feeds_v2.csv, CC0) and the latest dataset it mirrors for each GTFS Schedule feed with catalog status active, inactive, future. A feed is expired when the last date on which any of its services runs (calendar.txt and calendar_dates.txt) is before the as-of date, which is one day before the UTC run date so that it has passed in every time zone.

## Overall

| group | feeds | read | expired | expired share | expired over 1 year | ends within 30 days | ends in 30 days to 1 year | ends after 1 year |
|---|---|---|---|---|---|---|---|---|
| all | 3615 | 3503 | 700 | 20.0% | 395 | 143 | 2204 | 456 |

Read results: ok 3503, no_latest 69, no_service_dates 23, no_calendar 15, bad_zip 5.

## By catalog status

| group | feeds | read | expired | expired share | expired over 1 year | ends within 30 days | ends in 30 days to 1 year | ends after 1 year |
|---|---|---|---|---|---|---|---|---|
| active | 2880 | 2801 | 30 | 1.1% | 14 | 139 | 2179 | 453 |
| inactive | 721 | 688 | 670 | 97.4% | 381 | 3 | 14 | 1 |
| future | 14 | 14 | 0 | 0.0% | 0 | 1 | 11 | 2 |

## By catalog source (id prefix)

| group | feeds | read | expired | expired share | expired over 1 year | ends within 30 days | ends in 30 days to 1 year | ends after 1 year |
|---|---|---|---|---|---|---|---|---|
| mdb | 1876 | 1803 | 454 | 25.2% | 293 | 96 | 1011 | 242 |
| jbda | 584 | 580 | 43 | 7.4% | 0 | 14 | 505 | 18 |
| tdg | 565 | 549 | 54 | 9.8% | 14 | 14 | 425 | 56 |
| tld | 402 | 385 | 85 | 22.1% | 51 | 17 | 187 | 96 |
| ntd | 143 | 141 | 60 | 42.5% | 35 | 1 | 42 | 38 |
| odpt | 45 | 45 | 4 | 8.9% | 2 | 1 | 34 | 6 |

## By country (at least 10 feeds read), most expired first

| group | feeds | read | expired | expired share | expired over 1 year | ends within 30 days | ends in 30 days to 1 year | ends after 1 year |
|---|---|---|---|---|---|---|---|---|
| BR | 11 | 11 | 6 | 54.5% | 1 | 0 | 4 | 1 |
| IN | 17 | 17 | 6 | 35.3% | 3 | 0 | 7 | 4 |
| PL | 52 | 50 | 17 | 34.0% | 10 | 5 | 26 | 2 |
| BE | 13 | 13 | 4 | 30.8% | 1 | 0 | 8 | 1 |
| US | 1268 | 1230 | 353 | 28.7% | 232 | 44 | 609 | 224 |
| HU | 11 | 11 | 3 | 27.3% | 0 | 1 | 6 | 1 |
| AU | 40 | 36 | 9 | 25.0% | 8 | 0 | 27 | 0 |
| PT | 32 | 32 | 8 | 25.0% | 3 | 1 | 14 | 9 |
| DE | 49 | 42 | 10 | 23.8% | 6 | 2 | 30 | 0 |
| IT | 133 | 127 | 29 | 22.8% | 20 | 15 | 80 | 3 |
| BG | 15 | 14 | 3 | 21.4% | 0 | 1 | 8 | 2 |
| FI | 26 | 24 | 5 | 20.8% | 3 | 1 | 16 | 2 |
| ES | 155 | 150 | 27 | 18.0% | 10 | 10 | 97 | 16 |
| IE | 25 | 25 | 4 | 16.0% | 1 | 0 | 9 | 12 |
| TR | 23 | 21 | 3 | 14.3% | 1 | 0 | 18 | 0 |
| FR | 569 | 551 | 72 | 13.1% | 28 | 14 | 411 | 54 |
| CA | 154 | 150 | 19 | 12.7% | 17 | 7 | 96 | 28 |
| SE | 52 | 52 | 5 | 9.6% | 0 | 3 | 41 | 3 |
| NZ | 11 | 11 | 1 | 9.1% | 1 | 1 | 4 | 5 |
| JP | 633 | 629 | 48 | 7.6% | 2 | 15 | 541 | 25 |
| GB | 44 | 42 | 2 | 4.8% | 1 | 7 | 24 | 9 |
| EE | 27 | 27 | 0 | 0.0% | 0 | 0 | 15 | 12 |
| LT | 11 | 11 | 0 | 0.0% | 0 | 0 | 10 | 1 |
| LV | 12 | 12 | 0 | 0.0% | 0 | 1 | 11 | 0 |
| MY | 18 | 18 | 0 | 0.0% | 0 | 5 | 11 | 2 |
| RO | 31 | 27 | 0 | 0.0% | 0 | 0 | 21 | 6 |

67 other countries have fewer than 10 feeds read; see summary.json.

## Most common last days, feeds ending within a year

- all (2347 feeds): 12-31 409 (17.4%), 03-31 301 (12.8%), 08-31 74 (3.1%), 12-12 72 (3.1%), 09-30 71 (3.0%)
- JP (556 feeds): 03-31 285 (51.3%), 09-30 64 (11.5%), 12-31 20 (3.6%), 04-30 16 (2.9%), 11-30 9 (1.6%)
- US (653 feeds): 12-31 98 (15.0%), 02-01 46 (7.0%), 03-01 40 (6.1%), 01-01 25 (3.8%), 04-30 24 (3.7%)

## 事前に記録した予測 / Predictions recorded in advance

- X1: Of the feeds the catalog marks inactive that are read, at least 90% have no service left on the as-of date by their own calendar (the calendar agrees with the catalog status). Result: 97.4%, held.
- X2: Of all feeds read (active, inactive and future), between 12% and 25% are expired. Result: 20.0%, held.
- X3: Among expired inactive feeds, the median time since the last service date is more than 365 days. Result: 518 days, held.
- X4: Feeds in the United States are expired more often than feeds in Japan (one-sided Fisher exact test, p < 0.05). Result: p = 6.7e-29, held.
- X5: At least 80% of the inactive feeds can be read (the catalog still serves a dataset with service dates). Result: 95.4%, held.
- X6: Among expired feeds read that have a feed_info feed_end_date, at most 20% give a feed_end_date on or after the as-of date (feed_info still claiming validity after the last service day). Result: 6.1%, held.

Limits: the catalog's mirror can lag the publisher (a newer file at the publisher's own URL is not seen), and an entry may have been replaced by another. The catalog sets a feed inactive when its latest dataset's service date range has ended, so a census of active feeds alone undercounts expiry. Service dates are read from the calendar only: trips are not checked, so a service with no trips still counts, and removed dates are checked only at the end of each calendar range (services whose last 62 days are all removed are counted in tail_cut, not guessed). Countries are the catalog's. Counts are per catalog entry, not per agency or per rider.

Generated 2026-10-30T01:26:48Z. Made by MV2 of Munim, Inc. with AI agents working in MV2's name. Data CC BY 4.0; feed contents stay under their publishers' licences and are not redistributed.
