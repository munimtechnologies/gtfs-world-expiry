# mirror_check.py - compares the Mobility Database's mirror of each Japanese feed it imports from the GTFS Data
# Repository (https://gtfs-data.jp/; catalog ids jbda-...) with the file the repository serves itself. For every such
# catalog entry it says whether the mirror (urls.latest) holds the repository's current file (the same .txt members
# with the same CRC-32 and size, however the zip was packed), its next file, its previous file or none of them; how
# many days after the current file took effect the mirror was last written; whether the catalog status agrees with
# the repository; and which repository feeds have no catalog entry at all. Only zip directories and calendar.txt,
# calendar_dates.txt and feed_info.txt are read, through HTTP range requests (world_expiry.py). Predictions M1-M5
# (predictions-m-2026-10-24.md) were fixed before any file was read; they are scored on every run.
# Standard library only. MV2 of Munim, Inc. - Apache-2.0 license. Made with AI agents working in MV2's name.
import argparse
import collections
import csv
import datetime as dt
import email.utils
import json
import os
import re
import statistics
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import world_expiry as we  # noqa: E402

API = 'https://api.gtfs-data.jp/v2'
UA = 'gtfs-world-expiry mirror check (MV2 of Munim, Inc.; mv2@munimtech.com)'
JST = dt.timezone(dt.timedelta(hours=9))
OPEN_LICENCE = re.compile(r'^(CC[ -]?BY|CC0|PDL)', re.I)
URL_RE = re.compile(r'api\.gtfs-data\.jp/v2/organizations/([^/?#]+)/feeds/([^/?#]+)/files/feed\.zip(?:\?([^#]*))?')
HOLDS = ['current', 'next_1', 'prev_1', 'other', 'unread']
COLUMNS = ['id', 'mdb_status', 'provider', 'name', 'organization_id', 'feed_id', 'match_by', 'url_form',
           'source_listed', 'source_discontinued', 'source_license', 'source_listed_end', 'mirror_result',
           'mirror_modified', 'mirror_first', 'mirror_last', 'mirror_class', 'source_result', 'current_from',
           'current_to', 'current_published', 'current_since', 'later_files', 'next_from', 'next_published',
           'source_first', 'source_last', 'holds', 'mirror_lag_days', 'stale_days', 'source_running']
MISSING_COLUMNS = ['organization_id', 'feed_id', 'organization_name', 'feed_name', 'pref_id', 'license',
                   'listed_end']

# Fixed on 2026-10-24, before any mirror or repository file was read (predictions-m-2026-10-24.md).
PREDICTIONS_M = {
    'M1': 'Of the catalog entries with status active whose mirror and repository current file are both read, at '
          'least 85% hold the same file as the repository\'s current one.',
    'M2': 'No catalog entry\'s mirror holds a later file (next_1) of its repository feed, although some of those '
          'feeds have a later file already published.',
    'M3': 'Of the repository\'s feeds that are not discontinued, carry an open licence (CC BY, CC0 or PDL) and are '
          'listed with an end date on or after the as-of date, at least 90% have a jbda- entry in the catalog.',
    'M4': 'Of the catalog entries whose mirror has no service left on the as-of date, at least 75% have no service '
          'left at the repository either (no current file running on the as-of date, discontinued, or no longer '
          'listed).',
    'M5': 'Of the catalog entries with status active, at most 5% belong to a repository feed that is discontinued '
          'or no longer listed.',
}


def day(v):
    try:
        return dt.date.fromisoformat((v or '').strip()[:10])
    except ValueError:
        return None


def jst_day(ts):
    """'2026-08-31T15:27:50.278519+09:00' -> its date in Japan time."""
    if not ts:
        return None
    try:
        t = dt.datetime.fromisoformat(str(ts).replace('Z', '+00:00'))
    except ValueError:
        return day(ts)
    return (t.astimezone(JST) if t.tzinfo else t).date()


def http_day(v):
    """An HTTP date ('Thu, 01 Oct 2026 01:19:42 GMT') -> its UTC date, or None."""
    try:
        t = email.utils.parsedate_to_datetime(v)
    except (TypeError, ValueError, IndexError):
        return None
    if t is None:
        return None
    return (t.astimezone(dt.timezone.utc) if t.tzinfo else t).date()


def iso(d):
    return d.isoformat() if d else ''


def clean(text):
    return ' '.join(str(text or '').replace('|', '／').split())


def url_form(url):
    """-> (organization_id, feed_id, form) for a repository download URL; form is rid=<x>, uid, bare or other."""
    m = URL_RE.search(url or '')
    if not m:
        return '', '', 'other'
    q = urllib.parse.parse_qs(m.group(3) or '')
    form = f'rid={q["rid"][0]}' if 'rid' in q else 'uid' if 'uid' in q else 'bare'
    return urllib.parse.unquote(m.group(1)), urllib.parse.unquote(m.group(2)), form


def file_url(org, feed, rid):
    q = lambda s: urllib.parse.quote(s, safe='')  # noqa: E731
    return f'{API}/organizations/{q(org)}/feeds/{q(feed)}/files/feed.zip?rid={rid}'


def signature(z):
    """The .txt members as a sorted tuple of (lower-case base name, CRC-32, size): equal for two zips holding the
    same files, however they were packed."""
    sig = []
    for i in z.infolist():
        n = i.filename
        if n.startswith('__MACOSX') or n.endswith('/'):
            continue
        base = n.rsplit('/', 1)[-1].lower()
        if base.endswith('.txt'):
            sig.append((base, i.CRC, i.file_size))
    return tuple(sorted(sig))


def zip_facts(z):
    """-> {'sig', 'first_date', 'last_date', 'feed_end_date'} from an open zipfile.ZipFile; dates are None when the
    zip has no calendar."""
    out = {'sig': signature(z), 'first_date': None, 'last_date': None, 'feed_end_date': None}
    try:
        f = we.read_feed(z)
    except we.Skip:
        return out
    out.update({k: f[k] for k in ('first_date', 'last_date', 'feed_end_date')})
    return out


def open_zip(url, timeout=60, max_full=we.MAX_FULL):
    """-> (RangeFile over the zip at url, its Last-Modified header or ''). Like world_expiry.open_remote, but later
    range requests go to the final URL after redirects, so a repository download is requested once."""
    with we.http_get(url, f'bytes=-{we.TAIL}', timeout) as r:
        modified = r.headers.get('Last-Modified', '') or ''
        final = r.geturl() or url
        if r.status == 206:
            m = re.match(r'bytes (\d+)-(\d+)/(\d+)', r.headers.get('Content-Range', ''))
            if not m:
                raise we.Skip('bad_content_range')
            data = r.read()

            def fetch(lo, hi):
                with we.http_get(final, f'bytes={lo}-{hi}', timeout) as rr:
                    if rr.status != 206:
                        raise OSError(f'range ignored: HTTP {rr.status}')
                    return rr.read()
            return we.RangeFile(int(m.group(3)), fetch, int(m.group(1)), data), modified
        if int(r.headers.get('Content-Length') or 0) > max_full:
            raise we.Skip('too_big')
        data = r.read(max_full + 1)
        if len(data) > max_full:
            raise we.Skip('too_big')

    def no_fetch(lo, hi):
        raise OSError('no range support')
    f = we.RangeFile(len(data), no_fetch, 0, data)
    f.ranged = False
    return f, modified


def read_zip(url):
    """-> {'result', 'modified', 'sig', 'first_date', 'last_date', 'feed_end_date'} for the zip at url; result is
    'ok' or the reason it could not be read."""
    out = {'result': '', 'modified': '', 'sig': None, 'first_date': None, 'last_date': None, 'feed_end_date': None}
    try:
        f, out['modified'] = open_zip(url)
        with zipfile.ZipFile(f) as z:
            out.update(zip_facts(z))
        out['result'] = 'ok'
    except we.Skip as e:
        out['result'] = str(e)
    except urllib.error.HTTPError as e:
        out['result'] = f'http_{e.code}'
    except zipfile.BadZipFile:
        out['result'] = 'bad_zip'
    except (urllib.error.URLError, OSError, TimeoutError):
        out['result'] = 'network_error'
    except Exception as e:  # noqa: BLE001 - one bad file must not stop the check
        out['result'] = f'error_{type(e).__name__}'
    return out


def get_json(url):
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode('utf-8'))


def fetch_body(org, feed):
    """The body of the feed's API entry, or None."""
    q = lambda s: urllib.parse.quote(s, safe='')  # noqa: E731
    try:
        data = get_json(f'{API}/organizations/{q(org)}/feeds/{q(feed)}')
    except Exception:  # noqa: BLE001 - recorded as api_failed
        return None
    return data.get('body') if isinstance(data, dict) and data.get('code') == 200 else None


def feed_list(doc):
    """The API's /feeds answer ({'body': [...]}) or a bare list -> the feed dicts that have both ids."""
    body = doc.get('body') if isinstance(doc, dict) else doc
    return [f for f in body or [] if isinstance(f, dict) and f.get('organization_id') and f.get('feed_id')]


def discontinued(f):
    return f.get('feed_is_discontinued') in (True, 'true')


def jbda_rows(catalog_rows):
    """Catalog rows that come from the repository: GTFS rows whose id starts with jbda-."""
    return [r for r in catalog_rows if (r.get('data_type') or '').strip() == 'gtfs'
            and (r.get('id') or '').startswith('jbda-')]


def locate(row, by_key, by_id):
    """-> (organization_id, feed_id, match_by, url_form) for a catalog row: the repository ids in its download URL,
    or else the repository feed whose 'jbda-<organization>-<feed>' equals the catalog id."""
    org, feed, form = url_form(row.get('urls.direct_download'))
    if org and (org, feed) in by_key:
        return org, feed, 'url', form
    f = by_id.get((row.get('id') or '').lower())
    if f:
        return f['organization_id'], f['feed_id'], 'id', form
    if org:
        return org, feed, 'url_unlisted', form
    return '', '', 'none', form


def current_file(body):
    files = [x for x in (body or {}).get('gtfs_files') or [] if day(x.get('from_date')) and day(x.get('to_date'))]
    return next((x for x in files if x.get('rid') == 'current'), None), files


def check_entry(row, src, body, as_of, read, org='', feed='', match_by='none', form='other'):
    """One catalog row -> one mirror.csv row (dates as date objects). src is the repository list entry (None if the
    feed is not listed), body its API entry (None if not read). read(url) -> read_zip-style dict; repository files
    are read only for listed feeds, and the next and previous files only when the mirror differs from the current
    one."""
    out = {c: '' for c in COLUMNS}
    out.update({'id': row.get('id', ''), 'mdb_status': (row.get('status') or '').strip(),
                'provider': clean(row.get('provider'))[:120], 'name': clean(row.get('name'))[:120],
                'organization_id': org, 'feed_id': feed, 'match_by': match_by, 'url_form': form,
                'source_listed': 'yes' if src else 'no', 'holds': 'unread'})
    url = (row.get('urls.latest') or '').strip()
    m = read(url) if url else {'result': 'no_latest'}
    out['mirror_result'] = m['result']
    if m['result'] == 'ok':
        out.update({'mirror_modified': http_day(m.get('modified')), 'mirror_first': m['first_date'],
                    'mirror_last': m['last_date'], 'mirror_class': we.classify(m['last_date'], as_of)[1]})
    if not src:
        out['source_running'] = 'no'
        return out
    out.update({'source_discontinued': 'yes' if discontinued(src) else 'no',
                'source_license': src.get('feed_license') or '',
                'source_listed_end': day(src.get('latest_feed_end_date'))})
    cur, files = current_file(body)
    later = sorted((x for x in files if day(x['from_date']) > as_of), key=lambda x: day(x['from_date']))
    out['later_files'] = len(later) if body is not None else ''
    if later:
        out.update({'next_from': day(later[0]['from_date']), 'next_published': jst_day(later[0].get('published_at'))})
    if cur:
        since = max(day(cur['from_date']), jst_day(cur.get('published_at')) or day(cur['from_date']))
        out.update({'current_from': day(cur['from_date']), 'current_to': day(cur['to_date']),
                    'current_published': jst_day(cur.get('published_at')), 'current_since': since})
    running = (cur is not None and day(cur['from_date']) <= as_of <= day(cur['to_date'])
               and not discontinued(src))
    out['source_running'] = 'yes' if running else ('no' if body is not None or discontinued(src) else '')
    s = read(file_url(org, feed, 'current'))
    out['source_result'] = s['result']
    if s['result'] == 'ok':
        out.update({'source_first': s['first_date'], 'source_last': s['last_date']})
    if m['result'] != 'ok' or s['result'] != 'ok':
        return out
    if m['sig'] == s['sig']:
        out['holds'] = 'current'
        if cur and out['mirror_modified']:
            out['mirror_lag_days'] = (out['mirror_modified'] - out['current_since']).days
        return out
    out['holds'] = 'other'
    tries = (['next_1'] if later else []) + ['prev_1']
    for rid in tries:
        x = read(file_url(org, feed, rid))
        if x['result'] == 'ok' and x['sig'] == m['sig']:
            out['holds'] = rid
            break
    if out['holds'] != 'next_1' and cur:
        out['stale_days'] = (as_of - out['current_since']).days
    return out


def quartiles(xs):
    if not xs:
        return {'n': 0}
    xs = sorted(xs)
    q = statistics.quantiles(xs, n=4, method='inclusive') if len(xs) > 1 else [xs[0]] * 3
    return {'n': len(xs), 'min': xs[0], 'q1': q[0], 'median': statistics.median(xs), 'q3': q[2], 'max': xs[-1]}


def share(a, b):
    return round(a / b, 4) if b else None


def coverage(feeds, located, as_of):
    """-> (counts, missing rows) for the repository feeds in scope of M3: not discontinued, open licence, listed end
    on or after the as-of date."""
    scope = [f for f in feeds if not discontinued(f) and OPEN_LICENCE.match(f.get('feed_license') or '')
             and day(f.get('latest_feed_end_date')) and day(f.get('latest_feed_end_date')) >= as_of]
    missing = [f for f in scope if (f['organization_id'], f['feed_id']) not in located]
    rows = [{'organization_id': f['organization_id'], 'feed_id': f['feed_id'],
             'organization_name': clean(f.get('organization_name')), 'feed_name': clean(f.get('feed_name')),
             'pref_id': f.get('feed_pref_id') or '', 'license': f.get('feed_license') or '',
             'listed_end': f.get('latest_feed_end_date') or ''} for f in missing]
    return {'in_scope': len(scope), 'with_entry': len(scope) - len(missing), 'missing': len(missing)}, rows


def score_m(rows, cov):
    active = [r for r in rows if r['mdb_status'] == 'active']
    both = [r for r in active if r['holds'] != 'unread']
    m1 = share(sum(r['holds'] == 'current' for r in both), len(both))
    nxt = sum(r['holds'] == 'next_1' for r in rows)
    with_later = sum(1 for r in rows if r['later_files'] not in ('', 0))
    gone = [r for r in rows if r['mirror_class'] in we.EXPIRED]
    m4 = share(sum(r['source_running'] == 'no' for r in gone), len(gone))
    m5 = share(sum(r['source_listed'] == 'no' or r['source_discontinued'] == 'yes' for r in active), len(active))
    m3 = share(cov['with_entry'], cov['in_scope'])
    vals = {'M1': (m1, m1 is not None and m1 >= 0.85),
            'M2': (f'{nxt} of {with_later}', None if not with_later else nxt == 0),
            'M3': (m3, m3 is not None and m3 >= 0.90),
            'M4': (m4, m4 is not None and m4 >= 0.75),
            'M5': (m5, m5 is not None and m5 <= 0.05)}
    return {k: {'text': PREDICTIONS_M[k], 'value': v, 'held': None if v is None else h}
            for k, (v, h) in vals.items()}


def summarise(rows, cov, as_of, catalog_rows=0):
    lag = [r['mirror_lag_days'] for r in rows if r['mirror_lag_days'] != '']
    stale = [r['stale_days'] for r in rows if r['stale_days'] != '']
    lead = [(r['next_from'] - r['next_published']).days for r in rows if r['next_from'] and r['next_published']]
    s = {'as_of': iso(as_of), 'catalog_gtfs_rows': catalog_rows, 'entries': len(rows),
         'by_status': dict(collections.Counter(r['mdb_status'] for r in rows).most_common()),
         'match_by': dict(collections.Counter(r['match_by'] for r in rows).most_common()),
         'url_form': dict(collections.Counter(r['url_form'] for r in rows).most_common()),
         'mirror_results': dict(collections.Counter(r['mirror_result'] for r in rows).most_common()),
         'source_results': dict(collections.Counter(r['source_result'] or '(not read)' for r in rows).most_common()),
         'holds': {k: sum(r['holds'] == k for r in rows) for k in HOLDS},
         'holds_active': {k: sum(r['holds'] == k for r in rows if r['mdb_status'] == 'active') for k in HOLDS},
         'source_listed_no': sum(r['source_listed'] == 'no' for r in rows),
         'source_discontinued': sum(r['source_discontinued'] == 'yes' for r in rows),
         'mirror_expired': sum(r['mirror_class'] in we.EXPIRED for r in rows),
         'mirror_expired_source_running': sum(r['mirror_class'] in we.EXPIRED and r['source_running'] == 'yes'
                                              for r in rows),
         'with_later_file': sum(1 for r in rows if r['later_files'] not in ('', 0)),
         'later_lead_days': quartiles(lead), 'mirror_lag_days': quartiles(lag), 'stale_days': quartiles(stale),
         'coverage': cov}
    s['predictions'] = score_m(rows, cov)
    s['generated_at'] = dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    s['by'] = "MV2 of Munim, Inc. (made with AI agents working in MV2's name)"
    return s


def pct(x):
    return '' if x is None else f'{100 * x:.1f}%'


def q_line(q, unit='days'):
    if not q.get('n'):
        return 'none'
    return f'n {q["n"]}, median {q["median"]} {unit}, quartiles {q["q1"]}–{q["q3"]}, range {q["min"]}–{q["max"]}'


def report(rows, s):
    h, ha, c = s['holds'], s['holds_active'], s['coverage']
    lines = [f'# カタログのミラーと元のリポジトリ / The catalog\'s mirror against the source repository ({s["as_of"]})',
             '', 'Mobility Databaseが日本のGTFSデータリポジトリから取り込んだ各フィード（idがjbda-で始まるもの）について、'
             'カタログが保存している最新ファイルとリポジトリ自身が配る現行ファイルを比べました。',
             'For every feed the Mobility Database imports from Japan\'s GTFS Data Repository (catalog ids jbda-), the '
             'file the catalog mirrors (urls.latest) was compared with the file the repository serves itself '
             '(feed.zip?rid=current). Two files are the same when they hold the same .txt members with the same '
             'CRC-32 and size.', '',
             f'- catalog entries: {s["entries"]} ({", ".join(f"{k} {v}" for k, v in s["by_status"].items())})',
             f'- download URL forms: {", ".join(f"{k} {v}" for k, v in s["url_form"].items())}',
             f'- matched to the repository by: {", ".join(f"{k} {v}" for k, v in s["match_by"].items())}',
             f'- mirror holds (all entries): current {h["current"]}, next_1 {h["next_1"]}, prev_1 {h["prev_1"]}, '
             f'other {h["other"]}, unread {h["unread"]}',
             f'- mirror holds (status active): current {ha["current"]}, next_1 {ha["next_1"]}, prev_1 {ha["prev_1"]}, '
             f'other {ha["other"]}, unread {ha["unread"]}',
             f'- not listed in the repository any more: {s["source_listed_no"]}; discontinued there: '
             f'{s["source_discontinued"]}',
             f'- mirror has no service left: {s["mirror_expired"]}; of which the repository\'s current file still '
             f'runs: {s["mirror_expired_source_running"]}',
             f'- repository feeds with a later file already published: {s["with_later_file"]}; its lead time '
             f'(start minus publication, days): {q_line(s["later_lead_days"])}',
             f'- mirror written after the current file took effect (Last-Modified, UTC date, minus the later of the '
             f'file\'s start and its publication in Japan time; entries holding the current file): '
             f'{q_line(s["mirror_lag_days"])}',
             f'- entries holding an older or unknown file: days since the repository\'s current file took effect: '
             f'{q_line(s["stale_days"])}',
             f'- repository feeds in scope of M3 (not discontinued, open licence, listed end on or after the as-of '
             f'date): {c["in_scope"]}; with a catalog entry: {c["with_entry"]}; without: {c["missing"]} '
             f'(missing.csv)', '', '## 事前に記録した予測 / Predictions fixed before the run', '']
    for k, p in s['predictions'].items():
        v = p['value']
        shown = v if isinstance(v, str) else pct(v)
        verdict = {True: 'held', False: 'did not hold', None: 'could not be tested'}[p['held']]
        lines.append(f'- {k}: {p["text"]} Result: {shown or "none"}, {verdict}.')
    lines += ['', '## Entries whose mirror is not the repository\'s current file', '',
              '| id | status | holds | mirror last day | current from | current to | days since current | source '
              'running |', '|---|---|---|---|---|---|---|---|']
    for r in rows:
        if r['holds'] in ('next_1', 'prev_1', 'other'):
            lines.append(f'| {r["id"]} | {r["mdb_status"]} | {r["holds"]} | {iso(r["mirror_last"])} | '
                         f'{iso(r["current_from"])} | {iso(r["current_to"])} | {r["stale_days"]} | '
                         f'{r["source_running"]} |')
    lines += ['', 'Limits: one reading of each file on the day above; a file published or replaced that day can show '
              'as a difference. The mirror\'s Last-Modified header is taken as the day the catalog stored its latest '
              'file, which we have not confirmed with MobilityData. Only the next and the previous repository files '
              'are compared, so "other" can be an older file or one the repository no longer serves. The repository '
              'mostly holds municipal and regional operators; big-city operators that publish elsewhere are not in '
              'it. Counts are per catalog entry.', '',
              f'Generated {s["generated_at"]}. Sources: the Mobility Database catalog (feeds_v2.csv, CC0) and the GTFS '
              'Data Repository API v2 (https://gtfs-data.jp/). Feed contents stay under their publishers\' licences '
              'and are not redistributed. Made by MV2 of Munim, Inc. with AI agents working in MV2\'s name. Data CC '
              'BY 4.0.']
    return '\n'.join(lines) + '\n'


def csv_value(v):
    if v is None:
        return ''
    if isinstance(v, dt.date):
        return v.isoformat()
    return v


def write_csv(path, rows, columns):
    with open(path, 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=columns, extrasaction='ignore')
        w.writeheader()
        for r in rows:
            w.writerow({k: csv_value(r.get(k)) for k in columns})


def run(catalog_rows, feeds, as_of, read=read_zip, fetch=fetch_body, pause=1.0, log=sys.stdout):
    """(rows, coverage counts, missing rows). Every request to the repository waits `pause` seconds first."""
    by_key = {(f['organization_id'], f['feed_id']): f for f in feeds}
    by_id = {f'jbda-{f["organization_id"]}-{f["feed_id"]}'.lower(): f for f in feeds}

    def polite(fn):
        def call(*a):
            if pause:
                time.sleep(pause)
            return fn(*a)
        return call
    jp_fetch = polite(fetch)

    def jp_read(url):
        return polite(read)(url) if url.startswith(API) else read(url)

    rows, located = [], set()
    entries = jbda_rows(catalog_rows)
    t0 = time.time()
    for i, row in enumerate(entries, 1):
        org, feed, match_by, form = locate(row, by_key, by_id)
        src = by_key.get((org, feed))
        if src:
            located.add((org, feed))
        body = jp_fetch(org, feed) if src else None
        rows.append(check_entry(row, src, body, as_of, jp_read, org, feed, match_by, form))
        if i % 50 == 0 or i == len(entries):
            print(f'{i}/{len(entries)} entries, {time.time() - t0:.0f} s', file=log, flush=True)
    cov, missing = coverage(feeds, located, as_of)
    rows.sort(key=lambda r: r['id'])
    return rows, cov, missing


def main(argv=None, read=read_zip, fetch=fetch_body, feeds_doc=None):
    ap = argparse.ArgumentParser(description='Compare the Mobility Database mirror of Japanese feeds with the '
                                             'GTFS Data Repository.')
    ap.add_argument('--catalog', required=True, help='Mobility Database feeds_v2.csv')
    ap.add_argument('--feeds-json', help='a saved copy of the repository API\'s /feeds answer (default: fetch it)')
    ap.add_argument('--as-of', default='', help='YYYY-MM-DD (default: today in Japan)')
    ap.add_argument('--min-feeds', type=int, default=400, help='stop if the repository list has fewer feeds')
    ap.add_argument('--pause', type=float, default=1.0, help='seconds before each request to the repository')
    ap.add_argument('--out', required=True, help='results go to <out>/<as-of>/')
    a = ap.parse_args(argv)
    csv.field_size_limit(1 << 24)
    as_of = day(a.as_of) if a.as_of else dt.datetime.now(JST).date()
    if feeds_doc is None:
        if a.feeds_json:
            with open(a.feeds_json, encoding='utf-8') as f:
                feeds_doc = json.load(f)
        else:
            feeds_doc = get_json(f'{API}/feeds')
    feeds = feed_list(feeds_doc)
    if len(feeds) < a.min_feeds:
        sys.exit(f'the repository list has {len(feeds)} feeds, fewer than {a.min_feeds}')
    with open(a.catalog, encoding='utf-8-sig', newline='') as f:
        cat = list(csv.DictReader(f))
    print(f'{len(jbda_rows(cat))} jbda- catalog entries; {len(feeds)} repository feeds; as of {as_of}', flush=True)
    rows, cov, missing = run(cat, feeds, as_of, read, fetch, a.pause)
    s = summarise(rows, cov, as_of, sum((r.get('data_type') or '').strip() == 'gtfs' for r in cat))
    out = os.path.join(a.out, iso(as_of))
    os.makedirs(out, exist_ok=True)
    write_csv(os.path.join(out, 'mirror.csv'), rows, COLUMNS)
    write_csv(os.path.join(out, 'missing.csv'), missing, MISSING_COLUMNS)
    with open(os.path.join(out, 'summary.json'), 'w', encoding='utf-8') as f:
        json.dump(s, f, ensure_ascii=False, indent=1)
    with open(os.path.join(out, 'summary.md'), 'w', encoding='utf-8') as f:
        f.write(report(rows, s))
    print(json.dumps({k: s[k] for k in ('as_of', 'entries', 'holds', 'coverage', 'predictions')}, ensure_ascii=False))
    return s


if __name__ == '__main__':
    main()
