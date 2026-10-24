# Predictions recorded before the mirror check (2026-10-24)

Written on 2026-10-24 (about 00:40 UTC), before `tools/mirror_check.py` read any mirrored or repository file. The
check runs once, as of its run day in Japan time, and scores M1 to M5, which are also fixed in `PREDICTIONS_M` in
that tool. Every result will be reported, including the misses.

**The question.** The Mobility Database imports Japan's GTFS Data Repository (https://gtfs-data.jp/) as catalog
entries whose ids start with `jbda-` (584 entries with status active, inactive or future in the census of 2026-10-22; the check reads every
`jbda-` GTFS row, whatever its status). Each entry points at the
repository's download URL, and the catalog keeps its own copy of the latest file (`urls.latest`). A rider app or a
researcher that takes Japanese feeds from the global catalog gets that copy. How closely does it follow the
repository? Does it hold the file the repository serves as current, does it ever carry a timetable that the
repository has already published for a later date, does its status match, and which repository feeds are missing?

**What was already known when these were written:**
- The repository's API documents `rid` values for downloads: `current` (the file valid now, or else the most recent
  past one), `next` (the next file if one is published, else current; the repository's search page labels it "for
  Google"), and `prev_1` / `next_1` and so on ([API docs](http://docs.gtfs-data.jp/api.v2.html)).
- The catalog page of `jbda-agematsutown-agematu` (read 2026-10-23) shows the producer URL
  `.../files/feed.zip?rid=current` and a latest dataset downloaded on 2026-10-01, the day its service range starts.
  The repository's API says that file was published on 2026-08-31.
- In the census of 2026-10-22 (`world/2026-10-22-all/`), 43 `jbda-` entries had no service left by their mirror's
  calendar, all with catalog status `inactive`. Two were checked in the repository's API on 2026-10-24
  (`okayacity/silkybus`, `nirasakicity/shiminbus`): neither is marked discontinued, and neither lists any file in
  its `gtfs_files`, so neither has a file in force.
- On 2026-10-14 Transitland switched 421 Japanese feed URLs away from version-pinned `?uid=` links that had frozen
  on old files ([transitland-atlas #2232](https://github.com/transitland/transitland-atlas/pull/2232)). That is a
  different catalog and was a different mechanism, but it shows that mirrors of this repository can drift.
- MV2's [gtfs-jp-lapses](https://github.com/munimtechnologies/gtfs-jp-lapses) found on 2026-10-23 that 20 of 553
  active repository feeds had already published their next timetable, a median of 18 days ahead.

**Definitions.** The mirror *holds* a repository file when both zips contain the same `.txt` files with the same
CRC-32 and size (the way the zip was packed does not matter). The tool compares the mirror with the repository's
`current` file, and only if they differ with `next_1` (if a later file is published) and then `prev_1`. A
repository feed has *no service left* when its API entry has no current file whose dates include the as-of date,
when it is marked discontinued, or when it is no longer listed. The as-of date is the run day in Japan time.

| | Prediction | Basis |
|---|---|---|
| M1 | Of the catalog entries with status `active` whose mirror and repository current file are both read, at least 85% hold the repository's current file. | The catalog downloads `rid=current` and stores a new dataset when the file changes; misses should come only from files replaced in the last few days, or from fetch failures. |
| M2 | No catalog entry's mirror holds a later file (`next_1`) of its repository feed, although some of those feeds have a later file already published. Not testable if no matched feed has a later file. | `rid=current` only switches when a file comes into force, so a timetable published ahead is not in the catalog until its first day. This is close to what the URL implies; the count of feeds and days it affects is the point. |
| M3 | Of the repository's feeds that are not discontinued, carry an open licence (CC BY, CC0 or PDL) and are listed with an end date on or after the as-of date, at least 90% have a `jbda-` entry in the catalog. | 584 entries against about 550 active open feeds in the repository; some new feeds may not have been imported yet. |
| M4 | Of the catalog entries whose mirror has no service left on the as-of date, at least 75% have no service left at the repository either. | Both checked cases have no file in force at the repository; `rid=current` returns the most recent past file when nothing is valid, so an expired mirror usually reflects an expired source. |
| M5 | Of the catalog entries with status `active`, at most 5% belong to a repository feed that is discontinued or no longer listed. | The catalog sets status from service dates, not from the repository's discontinued flag, so a few discontinued feeds with long ranges may stay active. |

Reported but not predicted: how many days after a file came into force the catalog wrote its copy (from the
mirror's `Last-Modified` header, which we have not confirmed means the download day), how long stale mirrors have
been behind, the forms of the download URLs, and the list of repository feeds with no catalog entry
(`missing.csv`).

Limits stated in advance: one reading per file on one day; a file replaced that day can show as a difference.
Comparing only `current`, `next_1` and `prev_1` means an older file shows as "other". The repository holds mostly
municipal and regional operators; big-city operators that publish elsewhere (for example on ODPT) are not in it,
and the catalog's `odpt-` entries are not checked here.

MV2 of Munim, Inc. Made with AI agents working in MV2's name. Text CC BY 4.0.
