# Catalog status against the calendar, followed between two censuses

Before: data/before.csv (3615 feeds). After: /out/world/2026-10-29/feeds.csv (3615 feeds, 0 not in the first file).

A catalog status agrees with the calendar when an inactive feed has no service left, or an active or future feed has some. Groups are taken from the first census: inactive_running (inactive, service left), active_stuck (active, no service left for 30 days or more), active_recent (active, no service left for less).

| group | feeds | agree after | still disagree | not read after | gone (not in the after file) |
|---|---|---|---|---|---|
| inactive_running | 14 | 0 | 14 | 0 | 0 |
| active_stuck | 19 | 0 | 19 | 0 | 0 |
| active_recent | 5 | 0 | 5 | 0 | 0 |

Group sizes in each census: inactive_running 14 then 18, active_stuck 19 then 21, active_recent 5 then 9.

Status moves (before>after): active>active 2880, inactive>inactive 721, future>future 14.

## 事前に記録した予測 / Predictions recorded in advance

- Y1: Of the inactive_running feeds, at least 60% have a catalog status that agrees with their own calendar in the second census (the status catches up within about a week). Result: 0.0%, did not hold.
- Y2: Of the active_stuck feeds (active, no service left for 30 days or more), at least 80% still disagree in the second census (they are not updated within a week). Result: 100.0%, held.
- Y3: All six hand-checked active entries with no service date range on their catalog page (mdb-2234, tld-5769, mdb-912, mdb-3470, tdg-83969, tdg-84018) that are read in the second census still disagree. Result: 6 of 6, held.
- Y4: Both entries of the hand-checked seasonal feed whose range ended on 2026-10-20 (mdb-176, mdb-3211) that are read in the second census agree there. Result: 0 of 2, did not hold.
- Y5: In the second census, between 15 and 40 active entries have no service left (the stuck entries persist). Result: 30, held.
- Y6: In the second census, between 3 and 40 inactive entries still have service left (the lag recurs). Result: 18, held.

## Feeds followed

| group | id | country | before | after | outcome |
|---|---|---|---|---|---|
| active_stuck | mdb-1105 | PH | active, last day 2020-06-30 | active, last day 2020-06-30 | disagree |
| active_stuck | mdb-1106 | PH | active, last day 2020-06-30 | active, last day 2020-06-30 | disagree |
| active_stuck | mdb-1114 | FI | active, last day 2023-06-02 | active, last day 2023-06-02 | disagree |
| active_recent | mdb-176 | US | active, last day 2026-10-20 | active, last day 2026-10-20 | disagree |
| inactive_running | mdb-1830 | MX | inactive, last day 2026-12-31 | inactive, last day 2026-12-31 | disagree |
| inactive_running | mdb-1956 | GB | inactive, last day 2026-10-25 | inactive, last day 2026-11-01 | disagree |
| active_stuck | mdb-2234 | US | active, last day 2021-12-31 | active, last day 2021-12-31 | disagree |
| active_stuck | mdb-2235 | US | active, last day 2021-12-04 | active, last day 2021-12-04 | disagree |
| active_stuck | mdb-2236 | US | active, last day 2021-12-30 | active, last day 2021-12-30 | disagree |
| active_stuck | mdb-2238 | US | active, last day 2021-12-31 | active, last day 2021-12-31 | disagree |
| inactive_running | mdb-2666 | IT | inactive, last day 2026-11-20 | inactive, last day 2026-11-20 | disagree |
| inactive_running | mdb-2713 | ES | inactive, last day 2026-11-30 | inactive, last day 2026-11-30 | disagree |
| inactive_running | mdb-2819 | ES | inactive, last day 2026-11-25 | inactive, last day 2026-11-10 | disagree |
| inactive_running | mdb-2838 | PT | inactive, last day 2026-12-31 | inactive, last day 2026-12-31 | disagree |
| inactive_running | mdb-2867 | IN | inactive, last day 2027-08-30 | inactive, last day 2027-08-30 | disagree |
| inactive_running | mdb-3149 | US | inactive, last day 2027-05-28 | inactive, last day 2027-05-28 | disagree |
| active_recent | mdb-3211 | US | active, last day 2026-10-20 | active, last day 2026-10-20 | disagree |
| inactive_running | mdb-3226 | RU | inactive, last day 2030-12-31 | inactive, last day 2030-12-31 | disagree |
| active_stuck | mdb-3459 | EG | active, last day 2025-12-31 | active, last day 2025-12-31 | disagree |
| active_recent | mdb-3470 | FR | active, last day 2026-10-18 | active, last day 2026-10-18 | disagree |
| inactive_running | mdb-420 | US | inactive, last day 2027-04-15 | inactive, last day 2027-04-15 | disagree |
| active_stuck | mdb-912 | IT | active, last day 2022-12-31 | active, last day 2022-12-31 | disagree |
| active_stuck | ntd-50282 | US | active, last day 2025-12-31 | active, last day 2025-12-31 | disagree |
| inactive_running | tdg-81996 | FR | inactive, last day 2026-12-30 | inactive, last day 2026-12-30 | disagree |
| inactive_running | tdg-8201 | FR | inactive, last day 2026-12-31 | inactive, last day 2026-12-31 | disagree |
| inactive_running | tdg-82148 | FR | inactive, last day 2027-06-26 | inactive, last day 2027-06-26 | disagree |
| active_stuck | tdg-82289 | FR | active, last day 2026-07-04 | active, last day 2026-07-04 | disagree |
| active_recent | tdg-83969 | FR | active, last day 2026-09-30 | active, last day 2026-09-30 | disagree |
| active_recent | tdg-84018 | FR | active, last day 2026-09-27 | active, last day 2026-09-27 | disagree |
| inactive_running | tdg-84068 | FR | inactive, last day 2027-04-01 | inactive, last day 2027-04-01 | disagree |
| active_stuck | tld-4310 | SA | active, last day 2025-10-26 | active, last day 2025-10-26 | disagree |
| active_stuck | tld-4684 | CA | active, last day 2023-06-30 | active, last day 2023-06-30 | disagree |
| active_stuck | tld-4798 | US | active, last day 2024-01-01 | active, last day 2024-01-01 | disagree |
| active_stuck | tld-5769 | US | active, last day 2024-06-21 | active, last day 2024-06-21 | disagree |
| active_stuck | tld-6756 | CA | active, last day 2025-09-30 | active, last day 2025-09-30 | disagree |
| active_stuck | tld-7825 | PT | active, last day 2025-12-31 | active, last day 2025-12-31 | disagree |
| active_stuck | tld-7876 | PT | active, last day 2025-12-31 | active, last day 2025-12-31 | disagree |
| active_stuck | tld-7877 | PT | active, last day 2025-12-31 | active, last day 2025-12-31 | disagree |

Limits: both censuses read the catalog's mirror of each latest dataset, not the publisher's own URL. Service dates come from the calendar only. An entry that leaves the after file was deprecated, set to development or removed, and is counted as gone, not as agreeing.

Generated 2026-10-30T01:26:48Z. Made by MV2 of Munim, Inc. with AI agents working in MV2's name. Data CC BY 4.0.
