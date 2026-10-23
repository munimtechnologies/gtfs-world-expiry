# world_diff.py - compares two censuses made by world_expiry.py (feeds.csv before and after) and follows the feeds
# whose catalog status disagreed with their own calendar in the first one: inactive feeds that still had service left
# (inactive_running), and active feeds that had none, for 30 days or more (active_stuck) or for less (active_recent).
# For each it reports whether the two agree in the second census, plus every status move between the two files.
# Predictions Y1-Y6 (predictions-y-2026-10-23.md) were fixed before the second census was run; --predictions Y
# scores them.
# Standard library only. MV2 of Munim, Inc. - Apache-2.0 license. Made with AI agents working in MV2's name.
import argparse
import collections
import csv
import glob
import json
import os
import sys

EXPIRED = ('expired_over_1y', 'expired')
GROUPS = ('inactive_running', 'active_stuck', 'active_recent')
OUTCOMES = ('agree', 'disagree', 'unread', 'gone')
STUCK_DAYS = 30
COLUMNS = ['group', 'id', 'country', 'provider', 'before_status', 'before_last_date', 'before_class',
           'after_status', 'after_result', 'after_last_date', 'after_class', 'outcome']

# Hand-checked on mobilitydatabase.org on 2026-10-23, before the second census: active entries with no service left
# whose latest dataset shows no service date range, so the catalog's status job never updates them.
NO_RANGE_IDS = ('mdb-2234', 'tld-5769', 'mdb-912', 'mdb-3470', 'tdg-83969', 'tdg-84018')
# Same day: a seasonal feed whose latest dataset has a range ending 2026-10-20 (2026-10-21 in its history table),
# still active in the catalog file of 2026-10-23; mdb-3211 serves the same file.
RANGE_LAG_IDS = ('mdb-176', 'mdb-3211')

# Fixed on 2026-10-23 (predictions-y-2026-10-23.md), before the second census. Groups come from the first census
# (world/2026-10-22-all/feeds.csv). Shares are of the group's feeds that are in the second census and read there.
PREDICTIONS_Y = {
    'Y1': 'Of the inactive_running feeds, at least 60% have a catalog status that agrees with their own calendar in '
          'the second census (the status catches up within about a week).',
    'Y2': 'Of the active_stuck feeds (active, no service left for 30 days or more), at least 80% still disagree in '
          'the second census (they are not updated within a week).',
    'Y3': 'All six hand-checked active entries with no service date range on their catalog page (mdb-2234, '
          'tld-5769, mdb-912, mdb-3470, tdg-83969, tdg-84018) that are read in the second census still disagree.',
    'Y4': 'Both entries of the hand-checked seasonal feed whose range ended on 2026-10-20 (mdb-176, mdb-3211) that '
          'are read in the second census agree there.',
    'Y5': 'In the second census, between 15 and 40 active entries have no service left (the stuck entries persist).',
    'Y6': 'In the second census, between 3 and 40 inactive entries still have service left (the lag recurs).',
}


def load(path):
    with open(path, encoding='utf-8-sig', newline='') as f:
        return {r['id']: r for r in csv.DictReader(f)}


def resolve_after(path):
    """A feeds.csv path, or a census folder holding <as-of>/feeds.csv (the newest one is taken)."""
    if os.path.isdir(path):
        found = sorted(glob.glob(os.path.join(path, '*', 'feeds.csv')))
        if found:
            return found[-1]
        if os.path.exists(os.path.join(path, 'feeds.csv')):
            return os.path.join(path, 'feeds.csv')
        raise FileNotFoundError(f'no feeds.csv under {path}')
    return path


def read_ok(r):
    return r.get('result') == 'ok' and bool(r.get('class'))


def agrees(r):
    """True when the catalog status matches the calendar, False when not, None when the feed was not read."""
    if not read_ok(r):
        return None
    expired = r['class'] in EXPIRED
    if r.get('status') == 'inactive':
        return expired
    if r.get('status') in ('active', 'future'):
        return not expired
    return None


def group_of(r):
    if not read_ok(r):
        return ''
    expired = r['class'] in EXPIRED
    if r.get('status') == 'inactive' and not expired:
        return 'inactive_running'
    if r.get('status') == 'active' and expired:
        return 'active_stuck' if int(r['days_left']) <= -STUCK_DAYS else 'active_recent'
    return ''


def outcome(a):
    if a is None:
        return 'gone'
    ok = agrees(a)
    if ok is None:
        return 'unread'
    return 'agree' if ok else 'disagree'


def share(a, b):
    return round(a / b, 4) if b else None


def compare(before, after):
    """-> (transition rows, summary dict without predictions)."""
    rows = []
    for fid in sorted(before):
        b = before[fid]
        g = group_of(b)
        if not g:
            continue
        a = after.get(fid)
        rows.append({'group': g, 'id': fid, 'country': b.get('country', ''), 'provider': b.get('provider', ''),
                     'before_status': b.get('status', ''), 'before_last_date': b.get('last_date', ''),
                     'before_class': b.get('class', ''), 'after_status': a.get('status', '') if a else '',
                     'after_result': a.get('result', '') if a else '', 'after_last_date': a.get('last_date', '') if a
                     else '', 'after_class': a.get('class', '') if a else '', 'outcome': outcome(a)})
    by_group = {}
    for g in GROUPS:
        c = collections.Counter(r['outcome'] for r in rows if r['group'] == g)
        by_group[g] = {'feeds': sum(c.values()), **{o: c[o] for o in OUTCOMES}}
    moves = collections.Counter(f'{b.get("status", "")}>{after[fid].get("status", "") if fid in after else "gone"}'
                                for fid, b in before.items())
    s = {'before_feeds': len(before), 'after_feeds': len(after),
         'new_in_after': sum(fid not in before for fid in after),
         'groups_before': {g: sum(group_of(r) == g for r in before.values()) for g in GROUPS},
         'groups_after': {g: sum(group_of(r) == g for r in after.values()) for g in GROUPS},
         'outcomes': by_group, 'status_moves': dict(sorted(moves.items(), key=lambda x: (-x[1], x[0])))}
    return rows, s


def score_y(rows, s):
    def frac(g, want):
        c = s['outcomes'][g]
        return share(c[want], c['agree'] + c['disagree'])

    def ids(wanted, want):
        out = [r['outcome'] for r in rows if r['id'] in wanted and r['outcome'] in ('agree', 'disagree')]
        k = sum(o == want for o in out)
        return (f'{k} of {len(out)}', len(out) > 0 and k == len(out)) if out else (None, False)

    y1, y2 = frac('inactive_running', 'agree'), frac('active_stuck', 'disagree')
    ga = s['groups_after']
    y5 = ga['active_stuck'] + ga['active_recent']
    y6 = ga['inactive_running']
    vals = {'Y1': (y1, y1 is not None and y1 >= 0.60),
            'Y2': (y2, y2 is not None and y2 >= 0.80),
            'Y3': ids(NO_RANGE_IDS, 'disagree'),
            'Y4': ids(RANGE_LAG_IDS, 'agree'),
            'Y5': (y5, 15 <= y5 <= 40),
            'Y6': (y6, 3 <= y6 <= 40)}
    return {k: {'text': PREDICTIONS_Y[k], 'value': v, 'held': None if v is None else bool(h)}
            for k, (v, h) in vals.items()}


def shown(v):
    if v is None:
        return 'none'
    if isinstance(v, float):
        return f'{100 * v:.1f}%'
    return str(v)


def report(s, rows):
    lines = ['# Catalog status against the calendar, followed between two censuses', '',
             f'Before: {s["before"]} ({s["before_feeds"]} feeds). After: {s["after"]} ({s["after_feeds"]} feeds, '
             f'{s["new_in_after"]} not in the first file).', '',
             'A catalog status agrees with the calendar when an inactive feed has no service left, or an active or '
             'future feed has some. Groups are taken from the first census: inactive_running (inactive, service '
             f'left), active_stuck (active, no service left for {STUCK_DAYS} days or more), active_recent (active, '
             'no service left for less).', '',
             '| group | feeds | agree after | still disagree | not read after | gone (not in the after file) |',
             '|---|---|---|---|---|---|']
    for g in GROUPS:
        c = s['outcomes'][g]
        lines.append(f'| {g} | {c["feeds"]} | {c["agree"]} | {c["disagree"]} | {c["unread"]} | {c["gone"]} |')
    lines += ['', 'Group sizes in each census: ' + ', '.join(
        f'{g} {s["groups_before"][g]} then {s["groups_after"][g]}' for g in GROUPS) + '.', '',
        'Status moves (before>after): ' + ', '.join(f'{k} {v}' for k, v in s['status_moves'].items()) + '.']
    if 'predictions' in s:
        lines += ['', '## 事前に記録した予測 / Predictions recorded in advance', '']
        for k, p in s['predictions'].items():
            verdict = {True: 'held', False: 'did not hold', None: 'could not be tested'}[p['held']]
            lines.append(f'- {k}: {p["text"]} Result: {shown(p["value"])}, {verdict}.')
    lines += ['', '## Feeds followed', '', '| group | id | country | before | after | outcome |', '|---|---|---|---|---|---|']
    for r in rows:
        lines.append(f'| {r["group"]} | {r["id"]} | {r["country"]} | {r["before_status"]}, last day '
                     f'{r["before_last_date"]} | {r["after_status"] or "-"}, last day {r["after_last_date"] or "-"} | '
                     f'{r["outcome"]} |')
    lines += ['', 'Limits: both censuses read the catalog\'s mirror of each latest dataset, not the publisher\'s own '
              'URL. Service dates come from the calendar only. An entry that leaves the after file was deprecated, '
              'set to development or removed, and is counted as gone, not as agreeing.', '',
              f'Generated {s["generated_at"]}. Made by MV2 of Munim, Inc. with AI agents working in MV2\'s name. '
              'Data CC BY 4.0.']
    return '\n'.join(lines) + '\n'


def main(argv=None):
    import datetime as dt
    ap = argparse.ArgumentParser(description='Follow catalog-status disagreements between two world_expiry censuses.')
    ap.add_argument('--before', required=True, help='feeds.csv of the first census')
    ap.add_argument('--after', required=True, help='feeds.csv of the second census, or its census folder')
    ap.add_argument('--predictions', choices=['Y'], help='score Y1-Y6')
    ap.add_argument('--out', required=True)
    a = ap.parse_args(argv)
    csv.field_size_limit(1 << 24)
    after_path = resolve_after(a.after)
    before, after = load(a.before), load(after_path)
    rows, s = compare(before, after)
    s = {'before': a.before.replace(os.sep, '/'), 'after': after_path.replace(os.sep, '/'), **s}
    if a.predictions:
        s['predictions'] = score_y(rows, s)
    s['generated_at'] = dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    s['by'] = "MV2 of Munim, Inc. (made with AI agents working in MV2's name)"
    os.makedirs(a.out, exist_ok=True)
    with open(os.path.join(a.out, 'transitions.csv'), 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS)
        w.writeheader()
        w.writerows(rows)
    with open(os.path.join(a.out, 'diff.json'), 'w', encoding='utf-8') as f:
        json.dump(s, f, ensure_ascii=False, indent=1)
    with open(os.path.join(a.out, 'diff.md'), 'w', encoding='utf-8') as f:
        f.write(report(s, rows))
    print(json.dumps({k: s[k] for k in ('groups_before', 'groups_after', 'outcomes', 'predictions') if k in s},
                     ensure_ascii=False), file=sys.stdout)
    return s


if __name__ == '__main__':
    main()
