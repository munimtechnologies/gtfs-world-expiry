# カタログのミラーと元のリポジトリ / The catalog's mirror against the source repository (2026-10-24)

Mobility Databaseが日本のGTFSデータリポジトリから取り込んだ各フィード（idがjbda-で始まるもの）について、カタログが保存している最新ファイルとリポジトリ自身が配る現行ファイルを比べました。
For every feed the Mobility Database imports from Japan's GTFS Data Repository (catalog ids jbda-), the file the catalog mirrors (urls.latest) was compared with the file the repository serves itself (feed.zip?rid=current). Two files are the same when they hold the same .txt members with the same CRC-32 and size.

- catalog entries: 584 (active 539, inactive 45)
- download URL forms: rid=current 584
- matched to the repository by: url 580, url_unlisted 4
- mirror holds (all entries): current 541, next_1 0, prev_1 11, other 1, unread 31
- mirror holds (status active): current 525, next_1 0, prev_1 11, other 1, unread 2
- not listed in the repository any more: 4; discontinued there: 11
- mirror has no service left: 43; of which the repository's current file still runs: 13
- repository feeds with a later file already published: 20; its lead time (start minus publication, days): n 20, median 18.0 days, quartiles 10.0–28.0, range 4–113
- mirror written after the current file took effect (Last-Modified, UTC date, minus the later of the file's start and its publication in Japan time; entries holding the current file): n 541, median 0 days, quartiles 0.0–1.0, range -295–175
- entries holding an older or unknown file: days since the repository's current file took effect: n 12, median 0.0 days, quartiles 0.0–0.0, range 0–1
- repository feeds in scope of M3 (not discontinued, open licence, listed end on or after the as-of date): 553; with a catalog entry: 551; without: 2 (missing.csv)

## 事前に記録した予測 / Predictions fixed before the run

- M1: Of the catalog entries with status active whose mirror and repository current file are both read, at least 85% hold the same file as the repository's current one. Result: 97.8%, held.
- M2: No catalog entry's mirror holds a later file (next_1) of its repository feed, although some of those feeds have a later file already published. Result: 0 of 20, held.
- M3: Of the repository's feeds that are not discontinued, carry an open licence (CC BY, CC0 or PDL) and are listed with an end date on or after the as-of date, at least 90% have a jbda- entry in the catalog. Result: 99.6%, held.
- M4: Of the catalog entries whose mirror has no service left on the as-of date, at least 75% have no service left at the repository either (no current file running on the as-of date, discontinued, or no longer listed). Result: 69.8%, did not hold.
- M5: Of the catalog entries with status active, at most 5% belong to a repository feed that is discontinued or no longer listed. Result: 0.4%, held.

## Entries whose mirror is not the repository's current file

| id | status | holds | mirror last day | current from | current to | days since current | source running |
|---|---|---|---|---|---|---|---|
| jbda-hakusancity-hakusan_bus_meguru | active | other | 2027-03-15 | 2026-03-16 | 2027-03-15 | 1 | yes |
| jbda-kuma-bus-kuma-bus | active | prev_1 | 2027-01-24 | 2026-10-01 | 2027-01-25 | 0 | yes |
| jbda-kumamoto-toshibus-kumamoto-toshibus | active | prev_1 | 2027-01-24 | 2026-06-06 | 2027-01-25 | 0 | yes |
| jbda-kumamotodentetsu-kumamotodentetsu-bus | active | prev_1 | 2027-01-24 | 2026-09-01 | 2027-01-25 | 0 | yes |
| jbda-mie-kotsu-sancochusei | active | prev_1 | 2027-03-22 | 2026-10-07 | 2027-01-24 | 0 | yes |
| jbda-mie-kotsu-sancoiga | active | prev_1 | 2027-01-23 | 2026-10-01 | 2027-01-24 | 0 | yes |
| jbda-mie-kotsu-sancoinanki | active | prev_1 | 2027-02-23 | 2026-04-01 | 2027-01-24 | 0 | yes |
| jbda-mie-kotsu-sancoise | active | prev_1 | 2027-01-23 | 2026-10-01 | 2027-01-24 | 0 | yes |
| jbda-mie-kotsu-sancokuwana | active | prev_1 | 2027-01-23 | 2026-10-17 | 2027-01-24 | 0 | yes |
| jbda-mie-kotsu-sancomatsusaka | active | prev_1 | 2027-01-23 | 2026-10-01 | 2027-01-24 | 0 | yes |
| jbda-mie-kotsu-sancoshima | active | prev_1 | 2027-01-23 | 2026-10-01 | 2027-01-24 | 0 | yes |
| jbda-sankobus-sankobus | active | prev_1 | 2027-01-24 | 2026-10-01 | 2027-01-25 | 0 | yes |

Limits: one reading of each file on the day above; a file published or replaced that day can show as a difference. The mirror's Last-Modified header is taken as the day the catalog stored its latest file, which we have not confirmed with MobilityData. Only the next and the previous repository files are compared, so "other" can be an older file or one the repository no longer serves. The repository mostly holds municipal and regional operators; big-city operators that publish elsewhere are not in it. Counts are per catalog entry.

Generated 2026-10-24T01:14:28Z. Sources: the Mobility Database catalog (feeds_v2.csv, CC0) and the GTFS Data Repository API v2 (https://gtfs-data.jp/). Feed contents stay under their publishers' licences and are not redistributed. Made by MV2 of Munim, Inc. with AI agents working in MV2's name. Data CC BY 4.0.
