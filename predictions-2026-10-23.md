# Predictions recorded before the first census (2026-10-23)

Written on 2026-10-23, before `tools/world_expiry.py` read any dataset. The census job waits until this file is on
`main` before it starts. The same six statements are fixed in `PREDICTIONS` in the tool and are scored with
`--predictions`. Every result will be reported, including the misses.

**Definitions.** The census covers every row of the Mobility Database catalog (`feeds_v2.csv`) with
`data_type = gtfs` and `status = active`. For each one, the tool reads the latest dataset the catalog mirrors
(`urls.latest`). A feed is *read* when its `calendar.txt` or `calendar_dates.txt` gives at least one service date.
A feed's *last service date* is the latest date on which any service runs: a flagged weekday inside a calendar range
that is not removed in `calendar_dates.txt`, or a date added there. A feed is *expired* when that date is before the
as-of date. The as-of date is one day before the run's UTC date, so it has already passed in every time zone. Shares
are of the feeds read.

| | Prediction | Basis |
|---|---|---|
| W1 | Worldwide, between 10% and 40% of the active feeds read are expired. | ITS Feed's US census of 736 feeds (validated 2026-09-29) found the feed_info end date already passed in 123 (16.7%) and no trips in the next 7 days in 178 (24%). The catalog also keeps many entries imported from TransitFeeds that may no longer be maintained. |
| W2 | Feeds imported from TransitFeeds (ids `tfs-`) are expired more often than feeds added as `mdb-` (one-sided Fisher exact test, p < 0.05). | TransitFeeds stopped being updated; spot checks of `tfs-` pages show service ranges that ended years ago. |
| W3 | In Japan (country JP) at most 3% of the feeds read are expired. | MV2's own census of the GTFS Data Repository (gtfs-jp-lapses v0.9.0) found all 553 current, openly licensed feeds continuous to their listed end dates on 2026-10-23. Most Japanese entries in the catalog come from that repository. |
| W4 | Among feeds whose service ends within a year of the as-of date, the most common last day of the year is 12-31, with at least 10% of them. | Calendar-year timetables and placeholder end dates. |
| W5 | Among Japanese feeds whose service ends within a year, at least 25% end on 03-31. | Japan's fiscal year ends on March 31. In gtfs-jp-lapses, 121 of 203 lapses started on April 1. |
| W6 | In the United States (country US) between 8% and 30% of the feeds read are expired. | ITS Feed's 16.7% and 24% above; their figures are for validator notices on producer URLs, ours are for calendar dates on the catalog's mirror, so the range is wide. |

Limits stated in advance: the catalog's mirror can lag a publisher's own URL. A feed marked active may have been
replaced by another entry. Trips are not checked. Feeds that cannot be read (download errors, no calendar) are
counted separately and are not in the shares.

MV2 of Munim, Inc. Made with AI agents working in MV2's name. Text CC BY 4.0.
