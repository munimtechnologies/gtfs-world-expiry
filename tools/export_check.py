"""Re-read the Mobility Database's feeds_v2.csv and compare its GTFS statuses with the census read of 2026-10-30.

MV2 of Munim, Inc. Made with AI agents working in MV2's name. Apache-2.0. Standard library only.

Why: our follow-up census (world/2026-10-29/) found that no status changed between two reads of feeds_v2.csv, and we
reported that as mobility-feed-api#1881. MobilityData answered (2026-11-02) that feed statuses are refreshed daily
but feeds_v2.csv is exported only on Tuesdays and Fridays at 04:00 UTC, so our reads fell on the 2026-10-23 and
2026-10-27 exports, and that the 2026-10-30 export shows the expected statuses. This script checks that against a
fresh copy of the file: how many statuses moved since our read, and what the entries named in the answer show now.

Fix (2026-11-04): the census writes the class `expired_over_1y` for feeds whose service ended more than a year ago.
The first version treated only `expired` as expired, so it counted about 380 long-expired `inactive` feeds as
disagreeing with their calendar. Any class starting with `expired` now counts as expired. The status moves and the
checks C1 and C2 never depended on this.
"""
import argparse
import csv
import io
import json
import os
import time
import urllib.request

CATALOG = "https://files.mobilitydatabase.org/feeds_v2.csv"
BEFORE = ("https://raw.githubusercontent.com/munimtechnologies/gtfs-world-expiry/"
          "main/world/2026-10-29/feeds.csv")
UA = "gtfs-world-expiry export check - MV2 of Munim, Inc. (mv2@munimtech.com)"
NAMED = {"mdb-176": "inactive", "mdb-3211": "inactive", "mdb-3149": "active"}  # as stated for the 10-30 export
WEEKLY = "mdb-1956"  # stated active in the 10-30 export; reported only (its file is replaced every week)


def fetch(url, ua=UA):
    req = urllib.request.Request(url, headers={"User-Agent": ua})
    with urllib.request.urlopen(req, timeout=300) as r:
        head = {k: r.headers.get(k) for k in ("Last-Modified", "ETag", "Content-Length")}
        return r.read().decode("utf-8-sig"), head


def rows_of(text):
    return list(csv.DictReader(io.StringIO(text)))


def is_expired(cls):
    """The census's classes: expired, expired_over_1y, ends_within_30d, ends_within_1y, ends_1_2y, ends_after_2y."""
    return cls.startswith("expired")


def disagrees(status, cls):
    """The census's own rule: inactive with service left, or active with none."""
    return (status == "inactive" and not is_expired(cls)) or (status == "active" and is_expired(cls))


def compare(before_rows, after_rows):
    after = {r["id"]: r for r in after_rows if r.get("data_type", "gtfs") == "gtfs"}
    moves, missing, changed = {}, [], []
    for b in before_rows:
        a = after.get(b["id"])
        if a is None:
            missing.append(b["id"])
            continue
        key = "%s->%s" % (b["status"], a["status"])
        moves[key] = moves.get(key, 0) + 1
        if a["status"] != b["status"]:
            changed.append(b["id"])
    dis = [b for b in before_rows if b.get("class") and disagrees(b["status"], b["class"])]
    now_agree = [b["id"] for b in dis if b["id"] in after and not disagrees(after[b["id"]]["status"], b["class"])]
    return {"before": len(before_rows), "after_gtfs": len(after), "missing_after": len(missing),
            "status_changed": len(changed), "moves": dict(sorted(moves.items())),
            "disagreeing_before": len(dis), "of_those_now_agree_with_their_10_29_calendar": len(now_agree),
            "now_agree_ids": sorted(now_agree),
            "named": {i: (after[i]["status"] if i in after else None) for i in list(NAMED) + [WEEKLY]},
            "changed_ids": sorted(changed)}


def checks(res):
    """C1: some status moved since our read. C2: the three named entries show the stated status. mdb-1956 is only
    reported: its file is replaced every week, so a new dataset can make it active again at any export."""
    c = {"C1": res["status_changed"] >= 1,
         "C2": all(res["named"].get(i) == s for i, s in NAMED.items())}
    return {k: ("held" if v else "did not hold") for k, v in c.items()}


def export_day_of(last_modified):
    if not last_modified:
        return None
    try:
        return time.strftime("%Y-%m-%d", time.strptime(last_modified, "%a, %d %b %Y %H:%M:%S GMT"))
    except ValueError:
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--catalog", default=CATALOG)
    ap.add_argument("--before", default=BEFORE)
    ap.add_argument("--out", default="out/export")
    args = ap.parse_args()
    read_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    after_text, head = fetch(args.catalog)
    time.sleep(2)
    before_text, _ = fetch(args.before)
    day = export_day_of(head.get("Last-Modified"))
    res = compare(rows_of(before_text), rows_of(after_text))
    res.update({"read_at": read_at, "catalog_headers": head, "export_day": day, "checks": checks(res)})
    os.makedirs(args.out, exist_ok=True)
    with open(os.path.join(args.out, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(res, f, indent=1)
    lines = ["# feeds_v2.csv re-read against the census read of 2026-10-30 (the 2026-10-27 export)", "",
             "Read %s; file Last-Modified %s." % (read_at, head.get("Last-Modified")), "",
             "Checks: `%s`" % json.dumps(res["checks"]), "",
             "| | count |", "|---|---|",
             "| GTFS entries in our 2026-10-30 read | %d |" % res["before"],
             "| of those, missing from the new file | %d |" % res["missing_after"],
             "| of those, status changed | %d |" % res["status_changed"],
             "| status disagreeing with the census's class for 2026-10-29 | %d |" % res["disagreeing_before"],
             "| of those, status now matches that class | %d |" % res[
                 "of_those_now_agree_with_their_10_29_calendar"], "",
             "Status moves: `%s`" % json.dumps(res["moves"]), "",
             "Named entries now: `%s`" % json.dumps(res["named"])]
    with open(os.path.join(args.out, "summary.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(json.dumps({k: res[k] for k in ("status_changed", "moves", "named", "checks", "export_day",
                                          "disagreeing_before")}), flush=True)


if __name__ == "__main__":
    main()
