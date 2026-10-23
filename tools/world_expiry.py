# world_expiry.py - for every active GTFS Schedule feed in the Mobility Database catalog (feeds_v2.csv), reads the
# calendar of its latest dataset (the catalog's urls.latest mirror) and finds the last date on which any service runs,
# then counts, overall, by country and by catalog source, how many feeds have no service left on the as-of date.
# Only calendar.txt, calendar_dates.txt and feed_info.txt are read, through HTTP range requests on the zip, so a
# feed costs a few small requests instead of a full download. Predictions W1-W6 (predictions-2026-10-23.md) were
# fixed before any dataset was read and are scored with --predictions.
# Standard library only. MV2 of Munim, Inc. - Apache-2.0 license. Made with AI agents working in MV2's name.
import argparse
import collections
import concurrent.futures as cf
import csv
import datetime as dt
import io
import json
import math
import os
import re
import sys
import time
import urllib.error
import urllib.request
import zipfile

UA = 'gtfs-world-expiry/0.1 (MV2 of Munim, Inc.; mv2@munimtech.com)'
TAIL = 65536                  # first request: the last 64 KiB of the zip (end record and, usually, the directory)
MAX_AHEAD = 8 << 20           # sequential reads double up to 8 MiB per request
MAX_FULL = 64 << 20           # a server that ignores Range: read the whole zip only up to 64 MiB
MAX_MEMBER = 400 << 20        # skip a calendar file over 400 MiB uncompressed
TAIL_DAYS = 62                # removed dates kept per service: the last 62 days of its calendar range
ONE_DAY = dt.timedelta(days=1)
WEEKDAYS = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
EXPIRED = ('expired_over_1y', 'expired')
CURRENT = ('ends_within_30d', 'ends_within_1y')
FEED_COLUMNS = ['id', 'country', 'subdivision', 'provider', 'name', 'source', 'result', 'error', 'zip_bytes',
                'ranged', 'requests', 'bytes_read', 'services', 'first_date', 'last_date', 'feed_end_date',
                'days_left', 'class', 'end_md', 'tail_cut']
COUNT_KEYS = ['feeds', 'ok', 'expired', 'expired_over_1y', 'ends_within_30d', 'ends_within_1y', 'ends_1_2y',
              'ends_after_2y', 'expired_share']

# Fixed on 2026-10-23, before any dataset was read (predictions-2026-10-23.md). Shares are of the feeds whose
# calendar was read ('ok'); expired = last service date before the as-of date.
PREDICTIONS = {
    'W1': 'Worldwide, between 10% and 40% of the active feeds read have no service left on the as-of date.',
    'W2': 'Feeds imported from TransitFeeds (ids tfs-) are expired more often than feeds added as mdb- '
          '(one-sided Fisher exact test, p < 0.05).',
    'W3': 'In Japan (country JP) at most 3% of the feeds read are expired.',
    'W4': 'Among feeds whose service ends within a year of the as-of date, the most common last day of the year is '
          '12-31, with at least 10% of them.',
    'W5': 'Among Japanese feeds whose service ends within a year, at least 25% end on 03-31 (the end of the fiscal '
          'year).',
    'W6': 'In the United States (country US) between 8% and 30% of the feeds read are expired.',
}


class Skip(Exception):
    """A feed that cannot be read; the message is its result code."""


class RangeFile(io.RawIOBase):
    """A read-only, seekable file whose bytes come from fetch(lo, hi) (inclusive byte range), with one buffer.
    A read outside the buffer fetches at least `block` bytes; reads that continue the buffer double the request
    size up to max_ahead; a short read near the end fetches the last `block` bytes. Enough for zipfile."""

    def __init__(self, size, fetch, buf_start=0, buf=b'', block=TAIL, max_ahead=MAX_AHEAD):
        super().__init__()
        self.size, self.fetch, self.block, self.max_ahead = size, fetch, block, max_ahead
        self.buf_start, self.buf, self.pos, self.ahead = buf_start, buf, 0, block
        self.requests, self.bytes_read, self.ranged = 0, len(buf), True

    def readable(self):
        return True

    def seekable(self):
        return True

    def tell(self):
        return self.pos

    def seek(self, offset, whence=0):
        base = {0: 0, 1: self.pos, 2: self.size}[whence]
        if base + offset < 0:
            raise OSError('seek before the start of the file')
        self.pos = base + offset
        return self.pos

    def read(self, n=-1):
        if n is None or n < 0:
            n = self.size - self.pos
        n = max(0, min(n, self.size - self.pos))
        if not n:
            return b''
        lo, end = self.pos, self.pos + n
        if not (self.buf_start <= lo and end <= self.buf_start + len(self.buf)):
            sequential = lo == self.buf_start + len(self.buf)
            self.ahead = min(self.ahead * 2, self.max_ahead) if sequential else self.block
            hi = min(self.size, lo + max(n, self.ahead))
            if hi - lo < self.block:
                lo = max(0, hi - self.block)
            data = self.fetch(lo, hi - 1)
            if len(data) != hi - lo:
                raise OSError(f'range {lo}-{hi - 1}: got {len(data)} bytes')
            self.buf_start, self.buf = lo, data
            self.requests += 1
            self.bytes_read += len(data)
        i = self.pos - self.buf_start
        out = self.buf[i:i + n]
        self.pos += len(out)
        return out

    def readinto(self, b):
        data = self.read(len(b))
        b[:len(data)] = data
        return len(data)


def http_get(url, rng=None, timeout=60):
    headers = {'User-Agent': UA}
    if rng:
        headers['Range'] = rng
    return urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=timeout)


def open_remote(url, timeout=60, max_full=MAX_FULL):
    """-> RangeFile over the zip at url. The first request asks for its last TAIL bytes; a server that ignores Range
    sends the whole file, which is kept in memory up to max_full bytes."""
    with http_get(url, f'bytes=-{TAIL}', timeout) as r:
        if r.status == 206:
            m = re.match(r'bytes (\d+)-(\d+)/(\d+)', r.headers.get('Content-Range', ''))
            if not m:
                raise Skip('bad_content_range')
            data = r.read()

            def fetch(lo, hi):
                with http_get(url, f'bytes={lo}-{hi}', timeout) as rr:
                    if rr.status != 206:
                        raise OSError(f'range ignored: HTTP {rr.status}')
                    return rr.read()
            return RangeFile(int(m.group(3)), fetch, int(m.group(1)), data)
        if int(r.headers.get('Content-Length') or 0) > max_full:
            raise Skip('too_big')
        data = r.read(max_full + 1)
        if len(data) > max_full:
            raise Skip('too_big')

    def no_fetch(lo, hi):
        raise OSError('no range support')
    f = RangeFile(len(data), no_fetch, 0, data)
    f.ranged = False
    return f


def gdate(s):
    s = (s or '').strip().strip('"')
    if len(s) != 8 or not s.isdigit():
        return None
    try:
        return dt.date(int(s[:4]), int(s[4:6]), int(s[6:]))
    except ValueError:
        return None


def table(fh):
    """(column index by stripped lower-case name, row iterator) for a GTFS text file opened from the zip."""
    reader = csv.reader(io.TextIOWrapper(fh, encoding='utf-8-sig', errors='replace', newline=''))
    header = next(reader, [])
    return {h.strip().lstrip('﻿').lower(): i for i, h in enumerate(header)}, reader


def cell(rec, i):
    return rec[i].strip() if i is not None and i < len(rec) else ''


def read_calendar(idx, reader):
    """-> {service_id: (start, end, weekday flags)} for rows with a valid range."""
    cal = {}
    sid_i, a_i, b_i = idx.get('service_id'), idx.get('start_date'), idx.get('end_date')
    flag_i = [idx.get(d) for d in WEEKDAYS]
    for rec in reader:
        sid = cell(rec, sid_i)
        a, b = gdate(cell(rec, a_i)), gdate(cell(rec, b_i))
        if not sid or a is None or b is None or b < a:
            continue
        cal[sid] = (a, b, tuple(cell(rec, i) == '1' for i in flag_i))
    return cal


def read_calendar_dates(idx, reader, cal, window=TAIL_DAYS):
    """-> (first added date, last added date, services with an added date, removed dates by service). Removed
    dates are kept only for calendar services and only in the last `window` days of their range."""
    first = last = None
    services, removed = set(), collections.defaultdict(set)
    sid_i, d_i, t_i = idx.get('service_id'), idx.get('date'), idx.get('exception_type')
    for rec in reader:
        sid, d, t = cell(rec, sid_i), gdate(cell(rec, d_i)), cell(rec, t_i)
        if not sid or d is None:
            continue
        if t == '1':
            services.add(sid)
            if first is None or d < first:
                first = d
            if last is None or d > last:
                last = d
        elif t == '2' and sid in cal and 0 <= (cal[sid][1] - d).days < window:
            removed[sid].add(d)
    return first, last, services, removed


def first_active(start, end, flags):
    """First day in [start, end] on a flagged weekday (removed dates are not checked)."""
    d = start
    for _ in range(7):
        if d > end:
            return None
        if flags[d.weekday()]:
            return d
        d += ONE_DAY
    return None


def last_active(start, end, flags, removed=(), window=TAIL_DAYS):
    """-> (last day in [start, end] on a flagged weekday and not removed, cut). cut is True when every flagged day of
    the last `window` days was removed, so the service's last day is unknown (counted, not guessed)."""
    d = end
    for _ in range(window):
        if d < start:
            return None, False
        if flags[d.weekday()] and d not in removed:
            return d, False
        d -= ONE_DAY
    return None, any(flags)


def service_span(cal, cd=(None, None, set(), {})):
    """-> (first service date, last service date, number of services, services with an unknown last day)."""
    first_add, last_add, add_services, removed = cd
    firsts = [first_add] if first_add else []
    lasts = [last_add] if last_add else []
    cut = 0
    for sid, (a, b, flags) in cal.items():
        f = first_active(a, b, flags)
        if f:
            firsts.append(f)
        last, c = last_active(a, b, flags, removed.get(sid, ()))
        if last:
            lasts.append(last)
        cut += c
    return (min(firsts) if firsts else None, max(lasts) if lasts else None, len(set(cal) | add_services), cut)


def find_members(names):
    """{basename: path} for the GTFS files we read, preferring the shallowest path and ignoring __MACOSX."""
    found = {}
    for n in sorted(names, key=lambda x: (x.count('/'), x)):
        if n.startswith('__MACOSX') or n.endswith('/'):
            continue
        base = n.rsplit('/', 1)[-1].lower()
        if base in ('calendar.txt', 'calendar_dates.txt', 'feed_info.txt') and base not in found:
            found[base] = n
    return found


def read_feed(z):
    """-> dict of first_date, last_date, services, tail_cut, feed_end_date from an open zipfile.ZipFile."""
    m = find_members(z.namelist())
    if 'calendar.txt' not in m and 'calendar_dates.txt' not in m:
        raise Skip('no_calendar')
    for k in ('calendar.txt', 'calendar_dates.txt'):
        if k in m and z.getinfo(m[k]).file_size > MAX_MEMBER:
            raise Skip('member_too_big')
    cal, cd = {}, (None, None, set(), {})
    if 'calendar.txt' in m:
        with z.open(m['calendar.txt']) as fh:
            cal = read_calendar(*table(fh))
    if 'calendar_dates.txt' in m:
        with z.open(m['calendar_dates.txt']) as fh:
            idx, reader = table(fh)
            cd = read_calendar_dates(idx, reader, cal)
    first, last, services, cut = service_span(cal, cd)
    feed_end = None
    if 'feed_info.txt' in m and z.getinfo(m['feed_info.txt']).file_size < (1 << 20):
        with z.open(m['feed_info.txt']) as fh:
            idx, reader = table(fh)
            rec = next(reader, [])
            feed_end = gdate(cell(rec, idx.get('feed_end_date')))
    return {'first_date': first, 'last_date': last, 'services': services, 'tail_cut': cut,
            'feed_end_date': feed_end}


def classify(last, as_of):
    if last is None:
        return None, ''
    k = (last - as_of).days
    if k < -365:
        c = 'expired_over_1y'
    elif k < 0:
        c = 'expired'
    elif k < 30:
        c = 'ends_within_30d'
    elif k < 365:
        c = 'ends_within_1y'
    elif k < 730:
        c = 'ends_1_2y'
    else:
        c = 'ends_after_2y'
    return k, c


def source_of(feed_id):
    return feed_id.split('-', 1)[0] if '-' in feed_id else feed_id


def process_feed(row, as_of, opener=open_remote):
    """One catalog row -> one feeds.csv row (dates as date objects, days_left as int or None)."""
    fid = row.get('id', '')
    out = {'id': fid, 'country': row.get('location.country_code', '') or '',
           'subdivision': (row.get('location.subdivision_name', '') or '')[:60],
           'provider': (row.get('provider', '') or '')[:120], 'name': (row.get('name', '') or '')[:120],
           'source': source_of(fid), 'result': '', 'error': '', 'zip_bytes': None, 'ranged': '', 'requests': 0,
           'bytes_read': 0, 'services': None, 'first_date': None, 'last_date': None, 'feed_end_date': None,
           'days_left': None, 'class': '', 'end_md': '', 'tail_cut': None}
    url = (row.get('urls.latest') or '').strip()
    if not url:
        out['result'] = 'no_latest'
        return out
    f = None
    try:
        f = opener(url)
        out['zip_bytes'], out['ranged'] = f.size, 'yes' if f.ranged else 'no'
        with zipfile.ZipFile(f) as z:
            out.update(read_feed(z))
        if out['last_date'] is None:
            out['result'] = 'no_service_dates'
        else:
            out['result'] = 'ok'
            out['days_left'], out['class'] = classify(out['last_date'], as_of)
            out['end_md'] = out['last_date'].strftime('%m-%d')
    except Skip as e:
        out['result'] = str(e)
    except urllib.error.HTTPError as e:
        out['result'] = f'http_{e.code}'
    except zipfile.BadZipFile as e:
        out['result'], out['error'] = 'bad_zip', str(e)[:120]
    except (urllib.error.URLError, OSError, TimeoutError) as e:
        out['result'], out['error'] = 'network_error', str(e)[:120]
    except Exception as e:  # noqa: BLE001 - one bad feed must not stop the census
        out['result'], out['error'] = 'error', f'{type(e).__name__}: {e}'[:120]
    if f is not None:
        out['requests'], out['bytes_read'] = f.requests + 1, f.bytes_read
    return out


def share(a, b):
    return round(a / b, 4) if b else None


def counts(rs):
    ok = [r for r in rs if r['result'] == 'ok']
    c = collections.Counter(r['class'] for r in ok)
    exp = c['expired'] + c['expired_over_1y']
    return {'feeds': len(rs), 'ok': len(ok), 'expired': exp, 'expired_over_1y': c['expired_over_1y'],
            'ends_within_30d': c['ends_within_30d'], 'ends_within_1y': c['ends_within_1y'],
            'ends_1_2y': c['ends_1_2y'], 'ends_after_2y': c['ends_after_2y'], 'expired_share': share(exp, len(ok))}


def end_days(rs, top=10):
    """Most common last days (MM-DD) among the read feeds whose service ends within a year."""
    c = collections.Counter(r['end_md'] for r in rs if r['result'] == 'ok' and r['class'] in CURRENT)
    n = sum(c.values())
    return {'n': n, 'top': [[md, k, share(k, n)] for md, k in sorted(c.items(), key=lambda x: (-x[1], x[0]))[:top]]}


def md_share(rs, md):
    cur = [r for r in rs if r['result'] == 'ok' and r['class'] in CURRENT]
    return share(sum(r['end_md'] == md for r in cur), len(cur))


def fisher_greater(a, b, c, d):
    """One-sided Fisher exact p that a/(a+b) is greater than c/(c+d), to 6 significant figures."""
    n1, n2, k = a + b, c + d, a + c
    if not n1 or not n2:
        return None
    lo, hi = max(0, k - n2), min(k, n1)
    num = sum(math.comb(n1, x) * math.comb(n2, k - x) for x in range(max(a, lo), hi + 1))
    return float(f'{num / math.comb(n1 + n2, k):.6g}')


def group_by(rs, key):
    g = collections.defaultdict(list)
    for r in rs:
        g[r[key] or '??'].append(r)
    return g


def score(s, rows):
    o, ctry, src = s['overall'], s['by_country'], s['by_source']
    jp, us = ctry.get('JP'), ctry.get('US')
    tfs, mdb = src.get('tfs'), src.get('mdb')
    p2 = (fisher_greater(tfs['expired'], tfs['ok'] - tfs['expired'], mdb['expired'], mdb['ok'] - mdb['expired'])
          if tfs and mdb else None)
    top = s['end_days']['all']['top']
    w4 = (top[0][0], top[0][2]) if top else (None, None)
    w5 = md_share([r for r in rows if r['country'] == 'JP'], '03-31')
    e = o['expired_share']
    ej = jp['expired_share'] if jp else None
    eu = us['expired_share'] if us else None
    vals = {'W1': (e, e is not None and 0.10 <= e <= 0.40),
            'W2': (p2, p2 is not None and p2 < 0.05),
            'W3': (ej, ej is not None and ej <= 0.03),
            'W4': (f'{w4[0]} {w4[1]}', w4[0] == '12-31' and w4[1] is not None and w4[1] >= 0.10),
            'W5': (w5, w5 is not None and w5 >= 0.25),
            'W6': (eu, eu is not None and 0.08 <= eu <= 0.30)}
    return {k: {'text': PREDICTIONS[k], 'value': v, 'held': h} for k, (v, h) in vals.items()}


def summarise(rows, as_of, catalog_status=None, predictions=False):
    s = {'as_of': as_of.isoformat(), 'catalog_status': catalog_status or {},
         'results': dict(collections.Counter(r['result'] for r in rows).most_common()),
         'overall': counts(rows),
         'by_source': {k: counts(v) for k, v in sorted(group_by(rows, 'source').items())},
         'by_country': {k: counts(v) for k, v in sorted(group_by(rows, 'country').items())},
         'end_days': {'all': end_days(rows), 'JP': end_days([r for r in rows if r['country'] == 'JP']),
                      'US': end_days([r for r in rows if r['country'] == 'US'])},
         'ranged': dict(collections.Counter(r['ranged'] for r in rows if r['ranged'])),
         'bytes_read': sum(r['bytes_read'] for r in rows), 'zip_bytes': sum(r['zip_bytes'] or 0 for r in rows)}
    if predictions:
        s['predictions'] = score(s, rows)
    s['generated_at'] = dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    s['by'] = "MV2 of Munim, Inc. (made with AI agents working in MV2's name)"
    return s


def pct(x):
    return '' if x is None else f'{100 * x:.1f}%'


def count_row(name, c):
    return (f'| {name} | {c["feeds"]} | {c["ok"]} | {c["expired"]} | {pct(c["expired_share"])} | '
            f'{c["expired_over_1y"]} | {c["ends_within_30d"]} | {c["ends_within_1y"]} | '
            f'{c["ends_1_2y"] + c["ends_after_2y"]} |')


COUNT_HEAD = ['| group | active feeds | read | expired | expired share | expired over 1 year | ends within 30 days | '
              'ends in 30 days to 1 year | ends after 1 year |', '|---|---|---|---|---|---|---|---|---|']


def report(s, min_country=10):
    lines = [f'# Active GTFS feeds with no service left, worldwide, as of {s["as_of"]}', '',
             'Source: the Mobility Database catalog (feeds_v2.csv, CC0) and the latest dataset it mirrors for each '
             'active GTFS Schedule feed. A feed is expired when the last date on which any of its services runs '
             '(calendar.txt and calendar_dates.txt) is before the as-of date, which is one day before the UTC run '
             'date so that it has passed in every time zone.', '', '## Overall', ''] + COUNT_HEAD
    lines.append(count_row('all', s['overall']))
    lines += ['', 'Read results: ' + ', '.join(f'{k} {v}' for k, v in s['results'].items()) + '.', '',
              '## By catalog source (id prefix)', ''] + COUNT_HEAD
    for k, c in sorted(s['by_source'].items(), key=lambda x: -x[1]['feeds']):
        lines.append(count_row(k, c))
    lines += ['', f'## By country (at least {min_country} feeds read), most expired first', ''] + COUNT_HEAD
    big = [(k, c) for k, c in s['by_country'].items() if c['ok'] >= min_country]
    for k, c in sorted(big, key=lambda x: (-(x[1]['expired_share'] or 0), x[0])):
        lines.append(count_row(k, c))
    rest = [k for k, c in s['by_country'].items() if c['ok'] < min_country]
    lines += ['', f'{len(rest)} other countries have fewer than {min_country} feeds read; see summary.json.', '',
              '## Most common last days, feeds ending within a year', '']
    for k in ('all', 'JP', 'US'):
        e = s['end_days'][k]
        tops = ', '.join(f'{md} {n} ({pct(sh)})' for md, n, sh in e['top'][:5])
        lines.append(f'- {k} ({e["n"]} feeds): {tops}')
    if 'predictions' in s:
        lines += ['', '## 事前に記録した予測 / Predictions recorded in advance', '']
        for k, p in s['predictions'].items():
            v = p['value']
            shown = (v if isinstance(v, str) else ('' if v is None else (f'p = {v:.3g}' if k == 'W2' else pct(v))))
            lines.append(f'- {k}: {p["text"]} Result: {shown}, {"held" if p["held"] else "did not hold"}.')
    lines += ['', 'Limits: the catalog\'s mirror can lag the publisher (a newer file at the publisher\'s own URL is not '
              'seen), and a feed marked active may have been replaced by another entry. Service dates are read from '
              'the calendar only: trips are not checked, so a service with no trips still counts, and removed dates '
              'are checked only at the end of each calendar range (services whose last 62 days are all removed are '
              'counted in tail_cut, not guessed). Countries are the catalog\'s. Counts are per catalog entry, not per '
              'agency or per rider.', '',
              f'Generated {s["generated_at"]}. Made by MV2 of Munim, Inc. with AI agents working in MV2\'s name. '
              'Data CC BY 4.0; feed contents stay under their publishers\' licences and are not redistributed.']
    return '\n'.join(lines) + '\n'


def csv_value(v):
    if v is None:
        return ''
    if isinstance(v, dt.date):
        return v.isoformat()
    return v


def load_catalog(path):
    with open(path, encoding='utf-8-sig', newline='') as f:
        rows = list(csv.DictReader(f))
    gtfs = [r for r in rows if (r.get('data_type') or '').strip() == 'gtfs']
    status = dict(collections.Counter((r.get('status') or '').strip() or '(blank)' for r in gtfs).most_common())
    return [r for r in gtfs if (r.get('status') or '').strip() == 'active'], status


def run(catalog_rows, as_of, workers=4, pause=0.25, opener=open_remote, log=sys.stdout):
    out = [None] * len(catalog_rows)

    def one(i):
        r = process_feed(catalog_rows[i], as_of, opener)
        if pause:
            time.sleep(pause)
        return i, r

    t0 = time.time()
    with cf.ThreadPoolExecutor(max_workers=workers) as ex:
        for done, fut in enumerate(cf.as_completed([ex.submit(one, i) for i in range(len(catalog_rows))]), 1):
            i, r = fut.result()
            out[i] = r
            if done % 200 == 0 or done == len(catalog_rows):
                print(f'{done}/{len(catalog_rows)} feeds, {time.time() - t0:.0f} s', file=log, flush=True)
    return out


def write_outputs(rows, s, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, 'feeds.csv'), 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=FEED_COLUMNS)
        w.writeheader()
        for r in sorted(rows, key=lambda x: x['id']):
            w.writerow({k: csv_value(r[k]) for k in FEED_COLUMNS})
    with open(os.path.join(out_dir, 'by_country.csv'), 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.writer(f)
        w.writerow(['country'] + COUNT_KEYS)
        for k, c in s['by_country'].items():
            w.writerow([k] + [csv_value(c[x]) for x in COUNT_KEYS])
    with open(os.path.join(out_dir, 'summary.json'), 'w', encoding='utf-8') as f:
        json.dump(s, f, ensure_ascii=False, indent=1)
    with open(os.path.join(out_dir, 'summary.md'), 'w', encoding='utf-8') as f:
        f.write(report(s))


def main(argv=None):
    ap = argparse.ArgumentParser(description='Worldwide count of active GTFS feeds with no service left.')
    ap.add_argument('--catalog', required=True, help='Mobility Database feeds_v2.csv')
    ap.add_argument('--as-of', default='', help='YYYY-MM-DD (default: one day before today in UTC)')
    ap.add_argument('--workers', type=int, default=4)
    ap.add_argument('--pause', type=float, default=0.25, help='seconds each worker waits after a feed')
    ap.add_argument('--limit', type=int, default=0, help='read only the first N active feeds (for a trial)')
    ap.add_argument('--predictions', action='store_true', help='score W1-W6')
    ap.add_argument('--out', required=True, help='results go to <out>/<as-of>/')
    a = ap.parse_args(argv)
    csv.field_size_limit(1 << 24)
    as_of = (dt.date.fromisoformat(a.as_of) if a.as_of
             else dt.datetime.now(dt.timezone.utc).date() - ONE_DAY)
    cat, status = load_catalog(a.catalog)
    if a.limit:
        cat = cat[:a.limit]
    print(f'{len(cat)} active GTFS feeds; catalog status counts {status}; as of {as_of}', flush=True)
    rows = run(cat, as_of, a.workers, a.pause)
    s = summarise(rows, as_of, status, a.predictions)
    write_outputs(rows, s, os.path.join(a.out, as_of.isoformat()))
    print(json.dumps({k: s[k] for k in ('as_of', 'results', 'overall', 'predictions') if k in s},
                     ensure_ascii=False))
    return s


if __name__ == '__main__':
    main()
