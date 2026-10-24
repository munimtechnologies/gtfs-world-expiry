# source_check.py - compares the Mobility Database's copy of each GTFS feed's latest dataset (urls.latest) with the
# file at the producer's own download URL (urls.direct_download). Every entry whose copy has no service left on the
# as-of date is checked (the expired group), and so is a seeded random sample of the entries whose copy still has
# service (the control group). Two files are the same when they hold the same .txt members with the same CRC-32 and
# size (mirror_check.signature), however the zip was packed. When they differ, the producer file's own calendar says
# whether the catalog's copy is stale (the producer serves a file that still runs) or both have ended. Only zip
# directories and calendar.txt, calendar_dates.txt and feed_info.txt are read, through HTTP range requests where the
# server allows them (world_expiry.py); producer URLs that need a key are not read, and each producer host gets at
# most one new file per --host-pause seconds. Predictions S1-S5 (predictions-s-2026-10-24.md) were fixed before any
# file was read; they are scored on every run.
# Standard library only. MV2 of Munim, Inc. - Apache-2.0 license. Made with AI agents working in MV2's name.
import argparse
import collections
import concurrent.futures as cf
import csv
import datetime as dt
import json
import os
import random
import sys
import threading
import time
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mirror_check as mc  # noqa: E402
import world_expiry as we  # noqa: E402

READ = ('same_file', 'differs_running', 'differs_ended')
VERDICTS = ['same_file', 'differs_running', 'differs_ended', 'producer_no_dates', 'producer_unreadable',
            'auth_required', 'no_direct_url', 'not_checked']
COLUMNS = ['id', 'country', 'provider', 'status', 'source', 'redirect', 'group', 'mirror_result', 'mirror_modified',
           'mirror_last', 'mirror_class', 'producer_host', 'producer_result', 'producer_modified', 'producer_last',
           'producer_class', 'verdict', 'days_since_copy_ended', 'producer_ahead_days']
NO_FILE = {'result': 'no_latest', 'modified': '', 'sig': None, 'first_date': None, 'last_date': None,
           'feed_end_date': None}

# Fixed on 2026-10-24, before any producer file was read (predictions-s-2026-10-24.md). The expired group is the
# entries (statuses active, inactive, future) whose catalog copy is read and has no service left on the as-of date.
PREDICTIONS_S = {
    'S1': 'Of the expired-group entries whose producer URL needs no key, between 35% and 85% return a readable zip '
          'with service dates.',
    'S2': 'Of the expired-group entries whose producer file is read with service dates, at most 15% are stale '
          'copies: the producer\'s file differs from the catalog\'s copy and still has service on the as-of date.',
    'S3': 'Of the expired-group entries whose producer file is read with service dates and has no service left '
          'either, at least 80% hold the same file as the catalog\'s copy.',
    'S4': 'Of the control-group entries whose producer file is read with service dates, at least 80% hold the same '
          'file as the catalog\'s copy.',
    'S5': 'Among the expired-group producer URLs that need no key and cannot be read, HTTP 404 is the most common '
          'result (strictly more often than any other).',
}


class HostGate:
    """Spaces the files fetched from one host at least `interval` seconds apart, across threads."""

    def __init__(self, interval, clock=time.monotonic, sleep=time.sleep):
        self.interval, self.clock, self.sleep = interval, clock, sleep
        self.lock, self.next = threading.Lock(), {}

    def wait(self, url):
        if not self.interval:
            return
        host = (urllib.parse.urlsplit(url).hostname or '').lower()
        with self.lock:
            now = self.clock()
            t = max(now, self.next.get(host, now))
            self.next[host] = t + self.interval
        if t > now:
            self.sleep(t - now)


def auth_needed(row):
    """True when the catalog says the producer URL needs a key (urls.authentication_type other than blank or 0)."""
    v = (row.get('urls.authentication_type') or '').strip()
    if not v:
        return False
    try:
        return float(v) != 0
    except ValueError:
        return True


def share(a, b):
    return round(a / b, 4) if b else None


def parallel(n, fn, workers, label, log):
    """[fn(i)[1] for i in range(n)], run on `workers` threads; fn returns (i, result)."""
    out = [None] * n
    t0 = time.time()
    with cf.ThreadPoolExecutor(max_workers=max(1, workers)) as ex:
        futs = [ex.submit(fn, i) for i in range(n)]
        for done, fut in enumerate(cf.as_completed(futs), 1):
            i, r = fut.result()
            out[i] = r
            if done % 200 == 0 or done == n:
                print(f'{label}: {done}/{n}, {time.time() - t0:.0f} s', file=log, flush=True)
    return out


def assign_groups(rows, mirrors, as_of, control, seed):
    """-> 'expired', 'control' or '' for each row. Expired: the copy is read and its last service date is before the
    as-of date. Control: a seeded random sample (random.Random(seed).sample over the ids in sorted order) of up to
    `control` entries whose copy is read and still has service."""
    g = [''] * len(rows)
    current = []
    for i, m in enumerate(mirrors):
        if m['result'] != 'ok' or m['last_date'] is None:
            continue
        if m['last_date'] < as_of:
            g[i] = 'expired'
        else:
            current.append(i)
    current.sort(key=lambda i: rows[i].get('id', ''))
    for i in random.Random(seed).sample(current, min(max(control, 0), len(current))):
        g[i] = 'control'
    return g


def base_row(row, m, group, as_of):
    """One catalog row and the reading of its copy -> a sources.csv row without the producer columns."""
    out = {c: '' for c in COLUMNS}
    fid = row.get('id', '')
    out.update({'id': fid, 'country': row.get('location.country_code', '') or '',
                'provider': mc.clean(row.get('provider'))[:80], 'status': (row.get('status') or '').strip(),
                'source': we.source_of(fid), 'redirect': mc.clean(row.get('redirect.id'))[:60], 'group': group,
                'mirror_result': m['result'], 'verdict': 'not_checked'})
    if m['result'] == 'ok':
        out['mirror_modified'] = mc.http_day(m.get('modified'))
        if m['last_date']:
            out['mirror_last'] = m['last_date']
            out['mirror_class'] = we.classify(m['last_date'], as_of)[1]
            if group == 'expired':
                out['days_since_copy_ended'] = (as_of - m['last_date']).days
    return out


def compare(row, m, as_of, read):
    """The producer columns and the verdict for one checked entry; m is the reading of its copy."""
    out = {'producer_host': '', 'producer_result': '', 'producer_modified': None, 'producer_last': None,
           'producer_class': '', 'verdict': '', 'producer_ahead_days': ''}
    url = (row.get('urls.direct_download') or '').strip()
    if not url:
        out['verdict'] = 'no_direct_url'
        return out
    out['producer_host'] = (urllib.parse.urlsplit(url).hostname or '').lower()
    if auth_needed(row):
        out['verdict'] = 'auth_required'
        return out
    p = read(url)
    out['producer_result'] = p['result']
    if p['result'] != 'ok':
        out['verdict'] = 'producer_unreadable'
        return out
    out['producer_modified'] = mc.http_day(p.get('modified'))
    if p['last_date'] is None:
        out['verdict'] = 'producer_no_dates'
        return out
    out['producer_last'] = p['last_date']
    out['producer_class'] = we.classify(p['last_date'], as_of)[1]
    if m.get('last_date'):
        out['producer_ahead_days'] = (p['last_date'] - m['last_date']).days
    if p['sig'] == m['sig']:
        out['verdict'] = 'same_file'
    elif p['last_date'] >= as_of:
        out['verdict'] = 'differs_running'
    else:
        out['verdict'] = 'differs_ended'
    return out


def run(catalog_rows, as_of, read=mc.read_zip, control=300, seed=20261024, workers=4, pause=0.25, host_pause=1.0,
        log=sys.stdout, gate=None):
    """-> sources.csv rows sorted by id. First every copy is read (each worker pausing `pause` seconds after a
    file), then the producer URL of every expired-group and control-group entry."""
    def one_mirror(i):
        url = (catalog_rows[i].get('urls.latest') or '').strip()
        r = read(url) if url else dict(NO_FILE)
        if pause:
            time.sleep(pause)
        return i, r
    mirrors = parallel(len(catalog_rows), one_mirror, workers, 'copies', log)
    groups = assign_groups(catalog_rows, mirrors, as_of, control, seed)
    todo = [i for i, g in enumerate(groups) if g]
    gate = gate or HostGate(host_pause)

    def gated(url):
        gate.wait(url)
        return read(url)

    def one_producer(k):
        i = todo[k]
        return k, compare(catalog_rows[i], mirrors[i], as_of, gated)
    producers = parallel(len(todo), one_producer, workers, 'producers', log) if todo else []
    rows = [base_row(r, mirrors[i], groups[i], as_of) for i, r in enumerate(catalog_rows)]
    for k, i in enumerate(todo):
        rows[i].update(producers[k])
    rows.sort(key=lambda r: r['id'])
    return rows


def tally(rows, key):
    return dict(collections.Counter(r[key] for r in rows).most_common())


def verdict_counts(rows):
    c = collections.Counter(r['verdict'] for r in rows)
    return {k: c[k] for k in VERDICTS if k != 'not_checked'}


def failures(rows):
    return tally([r for r in rows if r['verdict'] == 'producer_unreadable'], 'producer_result')


def score_s(rows):
    e = [r for r in rows if r['group'] == 'expired']
    e_open = [r for r in e if r['verdict'] not in ('auth_required', 'no_direct_url')]
    e_read = [r for r in e if r['verdict'] in READ]
    s1 = share(len(e_read), len(e_open))
    s2 = share(sum(r['verdict'] == 'differs_running' for r in e_read), len(e_read))
    ended = [r for r in e_read if r['verdict'] != 'differs_running']
    s3 = share(sum(r['verdict'] == 'same_file' for r in ended), len(ended))
    c_read = [r for r in rows if r['group'] == 'control' and r['verdict'] in READ]
    s4 = share(sum(r['verdict'] == 'same_file' for r in c_read), len(c_read))
    top = sorted(failures(e_open).items(), key=lambda x: (-x[1], x[0]))
    s5 = f'{top[0][0]} {top[0][1]} of {sum(n for _, n in top)}' if top else None
    s5_held = bool(top) and top[0][0] == 'http_404' and (len(top) == 1 or top[1][1] < top[0][1])
    vals = {'S1': (s1, s1 is not None and 0.35 <= s1 <= 0.85),
            'S2': (s2, s2 is not None and s2 <= 0.15),
            'S3': (s3, s3 is not None and s3 >= 0.80),
            'S4': (s4, s4 is not None and s4 >= 0.80),
            'S5': (s5, s5_held)}
    return {k: {'text': PREDICTIONS_S[k], 'value': v, 'held': None if v is None else h}
            for k, (v, h) in vals.items()}


def summarise(rows, as_of, statuses=('active', 'inactive', 'future'), control=300, seed=20261024,
              catalog_status=None):
    e = [r for r in rows if r['group'] == 'expired']
    c = [r for r in rows if r['group'] == 'control']
    stale = [r for r in e if r['verdict'] == 'differs_running']
    s = {'as_of': as_of.isoformat(), 'statuses': list(statuses), 'catalog_status': catalog_status or {},
         'entries': len(rows), 'by_status': tally(rows, 'status'), 'mirror_results': tally(rows, 'mirror_result'),
         'groups': {'expired': len(e), 'control': len(c), 'control_asked': control, 'seed': seed},
         'expired_verdicts': verdict_counts(e), 'control_verdicts': verdict_counts(c),
         'expired_verdicts_by_status': {k: verdict_counts(v) for k, v in sorted(we.group_by(e, 'status').items())},
         'expired_verdicts_by_source': {k: verdict_counts(v) for k, v in sorted(we.group_by(e, 'source').items())},
         'expired_failures': failures(e), 'control_failures': failures(c),
         'expired_redirected': sum(bool(r['redirect']) for r in e),
         'stale': {'n': len(stale),
                   'days_since_copy_ended': mc.quartiles([r['days_since_copy_ended'] for r in stale]),
                   'producer_ahead_days': mc.quartiles([r['producer_ahead_days'] for r in stale
                                                        if r['producer_ahead_days'] != '']),
                   'producer_modified_days_before_as_of': mc.quartiles(
                       [(as_of - r['producer_modified']).days for r in stale if r['producer_modified']])}}
    s['predictions'] = score_s(rows)
    s['generated_at'] = dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    s['by'] = "MV2 of Munim, Inc. (made with AI agents working in MV2's name)"
    return s


def pct(x):
    return '' if x is None else f'{100 * x:.1f}%'


def vline(name, counts, n):
    return f'- {name} ({n}): ' + ', '.join(f'{k} {counts[k]}' for k in VERDICTS if k != 'not_checked')


def report(rows, s):
    g, st = s['groups'], s['stale']
    lines = [f'# The catalog\'s copy against the producer\'s own file ({s["as_of"]})', '',
             'For GTFS feeds in the Mobility Database catalog (statuses ' + ', '.join(s['statuses']) + '), the copy '
             'of the latest dataset the catalog serves (urls.latest) was compared with the file at the producer\'s '
             'own download URL (urls.direct_download). Every entry whose copy has no service left on the as-of date '
             f'was checked (expired group, {g["expired"]}), and a seeded random sample of {g["control"]} entries '
             f'whose copy still has service (control group; seed {g["seed"]}). Two files are the same when they '
             'hold the same .txt members with the same CRC-32 and size. A stale copy is one whose producer serves '
             'a different file that still has service.', '',
             f'- catalog entries read: {s["entries"]} ({", ".join(f"{k} {v}" for k, v in s["by_status"].items())})',
             f'- copies: {", ".join(f"{k} {v}" for k, v in s["mirror_results"].items())}',
             vline('expired group', s['expired_verdicts'], g['expired'])]
    for k, v in s['expired_verdicts_by_status'].items():
        lines.append('  ' + vline(f'status {k}', v, sum(v.values())))
    lines += [vline('control group', s['control_verdicts'], g['control']),
              '- producer URLs that could not be read, expired group: '
              + (', '.join(f'{k} {v}' for k, v in s['expired_failures'].items()) or 'none'),
              '- producer URLs that could not be read, control group: '
              + (', '.join(f'{k} {v}' for k, v in s['control_failures'].items()) or 'none'),
              f'- expired-group entries the catalog redirects to another entry: {s["expired_redirected"]}',
              f'- stale copies: {st["n"]}; days since the copy ran out: {mc.q_line(st["days_since_copy_ended"])}; '
              f'producer file runs later by: {mc.q_line(st["producer_ahead_days"])}; producer Last-Modified before '
              f'the as-of date: {mc.q_line(st["producer_modified_days_before_as_of"])}', '',
              '## By catalog source (id prefix), expired group', '']
    for k, v in s['expired_verdicts_by_source'].items():
        lines.append(vline(k, v, sum(v.values())))
    lines += ['', '## 事前に記録した予測 / Predictions fixed before the run', '']
    for k, p in s['predictions'].items():
        v = p['value']
        shown = v if isinstance(v, str) else pct(v)
        verdict = {True: 'held', False: 'did not hold', None: 'could not be tested'}[p['held']]
        lines.append(f'- {k}: {p["text"]} Result: {shown or "none"}, {verdict}.')
    lines += ['', '## Stale copies (expired group)', '',
              '| id | status | country | provider | copy\'s last day | producer\'s last day | producer Last-Modified | '
              'days since copy ended |', '|---|---|---|---|---|---|---|---|']
    for r in rows:
        if r['group'] == 'expired' and r['verdict'] == 'differs_running':
            lines.append(f'| {r["id"]} | {r["status"]} | {r["country"]} | {r["provider"][:60]} | '
                         f'{mc.iso(r["mirror_last"] or None)} | {mc.iso(r["producer_last"])} | '
                         f'{mc.iso(r["producer_modified"])} | {r["days_since_copy_ended"]} |')
    lines += ['', 'Limits: each file is read once, on one day; a producer that published a new file that day can '
              'show as a difference the catalog would pick up at its next daily check. A producer URL can serve a '
              'different file to the catalog\'s fetcher (blocking, geography, a changed URL the catalog has not '
              'recorded). Last-Modified headers are taken as given. Files that differ only in feed_info or other '
              'members count as different. Service dates come from the calendar files only. Counts are per catalog '
              'entry, not per agency, and a few files are catalogued twice.', '',
              f'Generated {s["generated_at"]}. Source: the Mobility Database catalog (feeds_v2.csv, CC0) and each '
              'producer\'s published file. Feed contents stay under their publishers\' licences and are not '
              'redistributed. Made by MV2 of Munim, Inc. with AI agents working in MV2\'s name. Data CC BY 4.0.']
    return '\n'.join(lines) + '\n'


def main(argv=None, read=mc.read_zip):
    ap = argparse.ArgumentParser(description='Compare the Mobility Database copy of each GTFS feed with the '
                                             'producer\'s own file.')
    ap.add_argument('--catalog', required=True, help='Mobility Database feeds_v2.csv')
    ap.add_argument('--statuses', default='active,inactive,future', help='comma-separated catalog statuses')
    ap.add_argument('--as-of', default='', help='YYYY-MM-DD (default: one day before today in UTC)')
    ap.add_argument('--control', type=int, default=300, help='size of the control sample')
    ap.add_argument('--seed', type=int, default=20261024)
    ap.add_argument('--workers', type=int, default=4)
    ap.add_argument('--pause', type=float, default=0.25, help='seconds each worker waits after reading a copy')
    ap.add_argument('--host-pause', type=float, default=1.0, help='seconds between two files from one producer host')
    ap.add_argument('--limit', type=int, default=0, help='read only the first N selected entries (for a trial)')
    ap.add_argument('--out', required=True, help='results go to <out>/<as-of>/')
    a = ap.parse_args(argv)
    csv.field_size_limit(1 << 24)
    as_of = (dt.date.fromisoformat(a.as_of) if a.as_of
             else dt.datetime.now(dt.timezone.utc).date() - we.ONE_DAY)
    statuses = tuple(x.strip() for x in a.statuses.split(',') if x.strip())
    cat, status = we.load_catalog(a.catalog, statuses)
    if a.limit:
        cat = cat[:a.limit]
    print(f'{len(cat)} GTFS entries with status {",".join(statuses)}; catalog status counts {status}; as of {as_of}',
          flush=True)
    rows = run(cat, as_of, read, a.control, a.seed, a.workers, a.pause, a.host_pause)
    s = summarise(rows, as_of, statuses, a.control, a.seed, status)
    out = os.path.join(a.out, as_of.isoformat())
    os.makedirs(out, exist_ok=True)
    mc.write_csv(os.path.join(out, 'sources.csv'), rows, COLUMNS)
    with open(os.path.join(out, 'summary.json'), 'w', encoding='utf-8') as f:
        json.dump(s, f, ensure_ascii=False, indent=1)
    with open(os.path.join(out, 'summary.md'), 'w', encoding='utf-8') as f:
        f.write(report(rows, s))
    print(json.dumps({k: s[k] for k in ('as_of', 'groups', 'expired_verdicts', 'control_verdicts', 'predictions')},
                     ensure_ascii=False))
    return s


if __name__ == '__main__':
    main()
