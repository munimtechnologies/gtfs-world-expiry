# Active GTFS feeds with no service left, worldwide, as of 2026-10-22

Source: the Mobility Database catalog (feeds_v2.csv, CC0) and the latest dataset it mirrors for each active GTFS Schedule feed. A feed is expired when the last date on which any of its services runs (calendar.txt and calendar_dates.txt) is before the as-of date, which is one day before the UTC run date so that it has passed in every time zone.

## Overall

| group | active feeds | read | expired | expired share | expired over 1 year | ends within 30 days | ends in 30 days to 1 year | ends after 1 year |
|---|---|---|---|---|---|---|---|---|
| all | 2880 | 2800 | 24 | 0.9% | 12 | 140 | 2201 | 435 |

Read results: ok 2800, no_latest 55, no_service_dates 15, no_calendar 10.

## By catalog source (id prefix)

| group | active feeds | read | expired | expired share | expired over 1 year | ends within 30 days | ends in 30 days to 1 year | ends after 1 year |
|---|---|---|---|---|---|---|---|---|
| mdb | 1391 | 1344 | 12 | 0.9% | 8 | 96 | 1000 | 236 |
| jbda | 539 | 537 | 0 | 0.0% | 0 | 13 | 508 | 16 |
| tdg | 502 | 490 | 3 | 0.6% | 0 | 17 | 418 | 52 |
| tld | 323 | 306 | 8 | 2.6% | 4 | 12 | 199 | 87 |
| ntd | 84 | 82 | 1 | 1.2% | 0 | 1 | 42 | 38 |
| odpt | 41 | 41 | 0 | 0.0% | 0 | 1 | 34 | 6 |

## By country (at least 10 feeds read), most expired first

| group | active feeds | read | expired | expired share | expired over 1 year | ends within 30 days | ends in 30 days to 1 year | ends after 1 year |
|---|---|---|---|---|---|---|---|---|
| PT | 26 | 26 | 3 | 11.5% | 0 | 1 | 13 | 9 |
| FI | 21 | 20 | 1 | 5.0% | 1 | 1 | 16 | 2 |
| CA | 135 | 132 | 2 | 1.5% | 2 | 5 | 104 | 21 |
| US | 909 | 879 | 9 | 1.0% | 6 | 41 | 606 | 223 |
| IT | 103 | 100 | 1 | 1.0% | 1 | 14 | 82 | 3 |
| FR | 487 | 475 | 4 | 0.8% | 0 | 17 | 403 | 51 |
| AU | 31 | 27 | 0 | 0.0% | 0 | 0 | 27 | 0 |
| BG | 13 | 12 | 0 | 0.0% | 0 | 2 | 8 | 2 |
| DE | 39 | 32 | 0 | 0.0% | 0 | 2 | 30 | 0 |
| EE | 27 | 27 | 0 | 0.0% | 0 | 2 | 13 | 12 |
| ES | 124 | 120 | 0 | 0.0% | 0 | 11 | 89 | 20 |
| GB | 41 | 39 | 0 | 0.0% | 0 | 9 | 19 | 11 |
| IE | 21 | 21 | 0 | 0.0% | 0 | 0 | 20 | 1 |
| IN | 10 | 10 | 0 | 0.0% | 0 | 0 | 6 | 4 |
| JP | 583 | 581 | 0 | 0.0% | 0 | 14 | 544 | 23 |
| LT | 11 | 11 | 0 | 0.0% | 0 | 0 | 10 | 1 |
| LV | 12 | 12 | 0 | 0.0% | 0 | 1 | 11 | 0 |
| MY | 18 | 18 | 0 | 0.0% | 0 | 5 | 11 | 2 |
| NZ | 10 | 10 | 0 | 0.0% | 0 | 0 | 5 | 5 |
| PL | 36 | 34 | 0 | 0.0% | 0 | 5 | 28 | 1 |
| RO | 28 | 24 | 0 | 0.0% | 0 | 0 | 18 | 6 |
| SE | 46 | 46 | 0 | 0.0% | 0 | 3 | 40 | 3 |
| TR | 20 | 18 | 0 | 0.0% | 0 | 0 | 18 | 0 |

52 other countries have fewer than 10 feeds read; see summary.json.

## Most common last days, feeds ending within a year

- all (2341 feeds): 12-31 416 (17.8%), 03-31 302 (12.9%), 08-31 73 (3.1%), 12-12 73 (3.1%), 09-30 71 (3.0%)
- JP (558 feeds): 03-31 287 (51.4%), 09-30 64 (11.5%), 12-31 20 (3.6%), 04-30 16 (2.9%), 12-28 9 (1.6%)
- US (647 feeds): 12-31 99 (15.3%), 02-01 46 (7.1%), 03-01 39 (6.0%), 01-01 25 (3.9%), 04-30 23 (3.5%)

## 事前に記録した予測 / Predictions recorded in advance

- W1: Worldwide, between 10% and 40% of the active feeds read have no service left on the as-of date. Result: 0.9%, did not hold.
- W2: Feeds imported from TransitFeeds (ids tfs-) are expired more often than feeds added as mdb- (one-sided Fisher exact test, p < 0.05). Result: , did not hold.
- W3: In Japan (country JP) at most 3% of the feeds read are expired. Result: 0.0%, held.
- W4: Among feeds whose service ends within a year of the as-of date, the most common last day of the year is 12-31, with at least 10% of them. Result: 12-31 0.1777, held.
- W5: Among Japanese feeds whose service ends within a year, at least 25% end on 03-31 (the end of the fiscal year). Result: 51.4%, held.
- W6: In the United States (country US) between 8% and 30% of the feeds read are expired. Result: 1.0%, did not hold.

Limits: the catalog's mirror can lag the publisher (a newer file at the publisher's own URL is not seen), and a feed marked active may have been replaced by another entry. Service dates are read from the calendar only: trips are not checked, so a service with no trips still counts, and removed dates are checked only at the end of each calendar range (services whose last 62 days are all removed are counted in tail_cut, not guessed). Countries are the catalog's. Counts are per catalog entry, not per agency or per rider.

Generated 2026-10-23T19:50:17Z. Made by MV2 of Munim, Inc. with AI agents working in MV2's name. Data CC BY 4.0; feed contents stay under their publishers' licences and are not redistributed.
