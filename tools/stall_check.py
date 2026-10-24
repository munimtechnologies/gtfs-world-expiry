# stall_check.py - follows up tools/source_check.py. It reads two sources.csv files: an earlier check (before; the
# published one of 2026-10-23) and a later run in which every entry whose copy still runs is checked (after; run
# source_check.py with --control larger than the catalog). It asks two things. Are the earlier stale copies still
# stale, or has the catalog stored a new copy since? And how many entries whose copy still runs have a stalled
# download: the producer serves a different file that still runs, whose Last-Modified day is after the day the catalog
# stored its copy and at least --min-days days before the as-of date? Predictions T1-T4 (predictions-t-2026-10-24.md)
# were fixed before the later run; they are scored on every run.
# Standard library only. MV2 of Munim, Inc. - Apache-2.0 license. Made with AI agents working in MV2's name.
import argparse
import collections
import csv
import datetime as dt
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mirror_check as mc  # noqa: E402
import source_check as sc  # noqa: E402

# The two months in which 10 of the 17 stale copies of 2026-10-23 were stored (found after that run, not predicted).
WINDOW = (dt.date(2026, 4, 19), dt.date(2026, 6, 18))
FATES = ['still_stale', 'no_new_copy_other', 'renewed', 'gone']
COLUMNS = ['id', 'kind', 'fate', 'country', 'provider', 'status', 'verdict', 'mirror_modified_before',
           'mirror_modified', 'mirror_last', 'producer_modified', 'producer_last', 'days_waiting', 'in_window']

# Fixed on 2026-10-24, before the later run (predictions-t-2026-10-24.md).
PREDICTIONS_T = {
    'T1': 'Of the earlier stale copies that are still in the catalog with a readable copy, at least 70% have no new '
          'copy in the later run: the catalog has stored no newer file (the copy\'s Last-Modified day and last service '
          'day are both unchanged).',
    'T2': 'Of the entries whose copy still runs and whose producer file is read with service dates, between 0.1% and '
          '2.0% have a stalled download.',
    'T3': 'Predictions S2, S3 and S4 of the source check hold again in the later run.',
    'T4': 'Among the entries with a stalled download, the catalog stored the copy between 2026-04-19 and 2026-06-18 '
          'more often than among the other entries whose copy still runs and whose producer file is read (one-sided '
          'Fisher exact p < 0.05; not tested with fewer than 5 stalled downloads).',
}


def read_rows(path):
    with open(path, encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def new_copy(b, a):
    """True when the catalog stored a newer copy between the two runs (b: before row, a: after row)."""
    mb, ma = mc.day(b['mirror_modified']), mc.day(a['mirror_modified'])
    return bool((mb and ma and ma > mb) or b['mirror_last'] != a['mirror_last'])


def fate(b, a):
    if a is None or a['mirror_result'] != 'ok':
        return 'gone'
    if new_copy(b, a):
        return 'renewed'
    return 'still_stale' if a['verdict'] == 'differs_running' else 'no_new_copy_other'


def live_read(r, as_of):
    """The copy still runs on the as-of date and the producer's file was read with service dates."""
    last = mc.day(r['mirror_last'])
    return bool(last and last >= as_of and r['verdict'] in sc.READ)


def stalled(r, as_of, min_days=3):
    """A copy that still runs, a producer file that differs and still runs, and a producer Last-Modified day after
    the day the catalog stored its copy and at least min_days days before the as-of date."""
    if not live_read(r, as_of) or r['verdict'] != 'differs_running':
        return False
    pm, mm = mc.day(r['producer_modified']), mc.day(r['mirror_modified'])
    return bool(pm and mm and pm > mm and (as_of - pm).days >= min_days)


def in_window(r):
    d = mc.day(r['mirror_modified'])
    return bool(d and WINDOW[0] <= d <= WINDOW[1])


def fisher_greater(a, b, c, d):
    """One-sided Fisher exact p for the table [[a, b], [c, d]]: the chance of a or more in the top-left cell with all
    margins fixed."""
    n, k, total = a + b, a + c, a + b + c + d
    den = math.comb(total, n)
    return sum(math.comb(k, x) * math.comb(total - k, n - x) for x in range(a, min(n, k) + 1)) / den


def word(held):
    return {True: 'held', False: 'did not hold', None: 'not tested'}[held]


def analyse(before, after, as_of, min_days=3):
    """-> (stalls.csv rows, summary dict)."""
    by_after = {r['id']: r for r in after}
    stale_before = [r for r in before if r['group'] == 'expired' and r['verdict'] == 'differs_running']
    before_ids = {r['id'] for r in stale_before}
    out = []
    fates = collections.Counter()
    for b in stale_before:
        a = by_after.get(b['id'])
        f = fate(b, a)
        fates[f] += 1
        row = dict(a if a is not None else b)
        row.update({'kind': 'stale_before', 'fate': f, 'mirror_modified_before': b['mirror_modified']})
        if a is None:
            row.update({'verdict': '', 'mirror_modified': '', 'mirror_last': '', 'producer_modified': '',
                        'producer_last': ''})
        out.append(row)
    live = [r for r in after if live_read(r, as_of)]
    stall = [r for r in live if stalled(r, as_of, min_days)]
    for r in stall:
        row = dict(r)
        row.update({'kind': 'stalled_live', 'fate': '', 'mirror_modified_before': '',
                    'days_waiting': (as_of - mc.day(r['producer_modified'])).days})
        out.append(row)
    stale_after = [r for r in after if r['group'] == 'expired' and r['verdict'] == 'differs_running']
    for r in stale_after:
        if r['id'] not in before_ids:
            row = dict(r)
            row.update({'kind': 'stale_new', 'fate': '', 'mirror_modified_before': ''})
            out.append(row)
    for row in out:
        row['in_window'] = int(in_window(row))
        if row['kind'] != 'stalled_live':
            row['days_waiting'] = ''
    out.sort(key=lambda r: (r['kind'], r['id']))

    present = len(stale_before) - fates['gone']
    kept = fates['still_stale'] + fates['no_new_copy_other']
    t1 = sc.share(kept, present)
    t2 = sc.share(len(stall), len(live))
    s = sc.score_s(after)
    t3_parts = {k: s[k]['held'] for k in ('S2', 'S3', 'S4')}
    t3 = (False if False in t3_parts.values() else None if None in t3_parts.values() else True)
    a_ = sum(in_window(r) for r in stall)
    others = [r for r in live if not stalled(r, as_of, min_days)]
    c_ = sum(in_window(r) for r in others)
    p4 = round(fisher_greater(a_, len(stall) - a_, c_, len(others) - c_), 6) if len(stall) >= 5 else None
    summary = {
        'as_of': as_of.isoformat(), 'min_days': min_days, 'window': [d.isoformat() for d in WINDOW],
        'stale_before': {'n': len(stale_before), 'fates': {k: fates[k] for k in FATES}},
        'live_read': len(live), 'stalled': len(stall),
        'stalled_days_waiting': mc.quartiles([(as_of - mc.day(r['producer_modified'])).days for r in stall]),
        'stalled_by_country': dict(collections.Counter(r['country'] for r in stall).most_common()),
        'window_counts': {'stalled_in_window': a_, 'stalled': len(stall), 'others_in_window': c_,
                          'others': len(others)},
        'stale_after': {'n': len(stale_after), 'new': sum(r['id'] not in before_ids for r in stale_after)},
        'predictions': {
            'T1': {'text': PREDICTIONS_T['T1'], 'value': t1, 'held': None if t1 is None else t1 >= 0.70},
            'T2': {'text': PREDICTIONS_T['T2'], 'value': t2, 'held': None if t2 is None else 0.001 <= t2 <= 0.02},
            'T3': {'text': PREDICTIONS_T['T3'], 'value': ', '.join(f'{k} {word(v)}' for k, v in t3_parts.items()),
                   'held': t3},
            'T4': {'text': PREDICTIONS_T['T4'], 'value': p4, 'held': None if p4 is None else p4 < 0.05},
        },
        'generated_at': dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'by': "MV2 of Munim, Inc. (made with AI agents working in MV2's name)",
    }
    return out, summary


def report(rows, s):
    st, w = s['stale_before'], s['window_counts']
    lines = [f'# Stale copies and stalled downloads ({s["as_of"]})', '',
             'A follow-up of the source check: are the earlier stale copies still stale, and how many entries whose '
             'copy still runs have a stalled download? A download is stalled when the producer serves a different '
             'file that still runs, whose Last-Modified day is after the day the catalog stored its copy and at '
             f'least {s["min_days"]} days before the as-of date.', '',
             f'- earlier stale copies: {st["n"]}; ' + ', '.join(f'{k} {v}' for k, v in st['fates'].items()),
             f'- entries whose copy still runs and whose producer file was read: {s["live_read"]}; stalled downloads: '
             f'{s["stalled"]}; days the producer file had been up: {mc.q_line(s["stalled_days_waiting"])}',
             '- stalled downloads by country: '
             + (', '.join(f'{k or "?"} {v}' for k, v in s['stalled_by_country'].items()) or 'none'),
             f'- copy stored {s["window"][0]} to {s["window"][1]}: stalled {w["stalled_in_window"]} of '
             f'{w["stalled"]}, other live entries read {w["others_in_window"]} of {w["others"]}',
             f'- stale copies in this run: {s["stale_after"]["n"]}, of which {s["stale_after"]["new"]} were not '
             'stale in the earlier check', '',
             '## 事前に記録した予測 / Predictions fixed before the run', '']
    for k, p in s['predictions'].items():
        v = p['value']
        shown = v if isinstance(v, str) else (f'p = {v:.3g}' if k == 'T4' and v is not None else sc.pct(v))
        lines.append(f'- {k}: {p["text"]} Result: {shown or "none"}, {word(p["held"])}.')
    lines += ['', '## Entries', '', '| id | kind | fate | country | provider | copy stored before | copy stored | '
              'copy\'s last day | producer Last-Modified | producer\'s last day | days waiting |',
              '|---|---|---|---|---|---|---|---|---|---|---|']
    for r in rows:
        lines.append(f'| {r["id"]} | {r["kind"]} | {r["fate"]} | {r["country"]} | {r["provider"][:50]} | '
                     f'{r["mirror_modified_before"]} | {r["mirror_modified"]} | {r["mirror_last"]} | '
                     f'{r["producer_modified"]} | {r["producer_last"]} | {r["days_waiting"]} |')
    lines += ['', 'Limits: each producer URL is read once, from one place, and the catalog\'s fetcher may be served '
              'differently. Last-Modified headers are taken as given; a producer that sends none is never counted as '
              'stalled. Counts are per catalog entry, not per agency.', '',
              f'Generated {s["generated_at"]}. Source: the Mobility Database catalog (feeds_v2.csv, CC0) and each '
              'producer\'s published file. Made by MV2 of Munim, Inc. with AI agents working in MV2\'s name. Data '
              'CC BY 4.0.']
    return '\n'.join(lines) + '\n'


def main(argv=None):
    ap = argparse.ArgumentParser(description='Follow up the source check: stale copies and stalled downloads.')
    ap.add_argument('--before', required=True, help='sources.csv of the earlier source check')
    ap.add_argument('--after', required=True, help='sources.csv of the later source check (every live entry read)')
    ap.add_argument('--as-of', required=True, help='YYYY-MM-DD, the as-of date of the later check')
    ap.add_argument('--min-days', type=int, default=3)
    ap.add_argument('--out', required=True, help='results go to <out>/<as-of>/')
    a = ap.parse_args(argv)
    csv.field_size_limit(1 << 24)
    as_of = dt.date.fromisoformat(a.as_of)
    rows, s = analyse(read_rows(a.before), read_rows(a.after), as_of, a.min_days)
    out = os.path.join(a.out, as_of.isoformat())
    os.makedirs(out, exist_ok=True)
    mc.write_csv(os.path.join(out, 'stalls.csv'), rows, COLUMNS)
    with open(os.path.join(out, 'summary.json'), 'w', encoding='utf-8') as f:
        json.dump(s, f, ensure_ascii=False, indent=1)
    with open(os.path.join(out, 'summary.md'), 'w', encoding='utf-8') as f:
        f.write(report(rows, s))
    print(json.dumps({k: s[k] for k in ('as_of', 'stale_before', 'live_read', 'stalled', 'predictions')},
                     ensure_ascii=False))
    return s


if __name__ == '__main__':
    main()
