# Tests for mirror_check.py on made-up zips and API answers served from memory. Every expected value is worked by
# hand. MV2 of Munim, Inc. - Apache-2.0 license. Made with AI agents working in MV2's name.
import csv
import datetime as dt
import io
import json
import os
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mirror_check as mc  # noqa: E402

AS_OF = dt.date(2026, 10, 24)
HEAD = 'service_id,monday,tuesday,wednesday,thursday,friday,saturday,sunday,start_date,end_date\n'
AGENCY = 'agency_id,agency_name,agency_url,agency_timezone\nA,Bus,https://example.jp/,Asia/Tokyo\n'


def make_zip(files, folder='', method=zipfile.ZIP_DEFLATED):
    b = io.BytesIO()
    with zipfile.ZipFile(b, 'w', method) as z:
        for n, t in files.items():
            z.writestr(folder + n, t)
    return b.getvalue()


def gtfs(start, end, extra=None):
    files = {'agency.txt': AGENCY, 'calendar.txt': HEAD + f'S1,1,1,1,1,1,1,1,{start},{end}\n'}
    files.update(extra or {})
    return files


# Every service runs daily, so the first and last service dates are the calendar range ends.
CAL_A = gtfs('20261001', '20270930')                                   # 2026-10-01 .. 2027-09-30
CAL_A2 = gtfs('20261001', '20270930', {'stops.txt': 'stop_id\nX\n'})   # same dates, one more member
CAL_C = gtfs('20260401', '20261031')                                   # ends in 7 days
CAL_NEXT = gtfs('20261101', '20271031')
CAL_D = gtfs('20261015', '20270331')
CAL_OLD2 = gtfs('20251015', '20261014')                                # expired 10 days before AS_OF
CAL_OLD = gtfs('20251001', '20260930')                                 # expired 24 days before AS_OF
CAL_E = gtfs('20260401', '20270331')


def mirror(fid):
    return f'https://files.mobilitydatabase.org/{fid}/latest.zip'


def direct(org, feed, query='?rid=current'):
    return f'https://api.gtfs-data.jp/v2/organizations/{org}/feeds/{feed}/files/feed.zip{query}'


def feed(org, fid, lic='CC BY 4.0', end='2027-03-31', disc=False):
    return {'organization_id': org, 'feed_id': fid, 'organization_name': f'{org} 市', 'feed_name': f'{fid} バス',
            'feed_pref_id': 20, 'feed_license': lic, 'latest_feed_end_date': end, 'feed_is_discontinued': disc}


FEEDS = [feed('town-a', 'bus', end='2027-09-30'), feed('cityb', 'loop', 'CC0 1.0', '2027-10-31'),
         feed('townc', 'demand'), feed('oldtown', 'line', end='2026-03-31', disc=True), feed('vill', 'e'),
         feed('closed', 'f', lic='その他'), feed('ended', 'g', end='2026-03-31'), feed('kita', 'mini'),
         feed('minami', 'bus', end='2027-10-31')]


def cur(a, b, pub, rid='current'):
    return {'rid': rid, 'from_date': a, 'to_date': b, 'published_at': pub}


BODIES = {
    ('town-a', 'bus'): {'gtfs_files': [cur('2026-10-01', '2027-09-30', '2026-08-31T15:27:50.278519+09:00')]},
    ('cityb', 'loop'): {'gtfs_files': [cur('2026-04-01', '2026-10-31', '2026-03-20T09:00:00+09:00'),
                                       cur('2026-11-01', '2027-10-31', '2026-10-10T10:00:00+09:00', 'next_1')]},
    ('townc', 'demand'): {'gtfs_files': [cur('2026-10-15', '2027-03-31', '2026-10-14T18:00:00+09:00')]},
    ('oldtown', 'line'): {'is_discontinued': True, 'gtfs_files': []},
    ('kita', 'mini'): {'gtfs_files': [cur('2026-04-01', '2027-03-31', '2026-03-01T12:00:00+09:00')]},
    ('minami', 'bus'): {'gtfs_files': [cur('2026-04-01', '2026-10-31', '2026-03-25T10:00:00+09:00'),
                                       cur('2026-11-01', '2027-10-31', '2026-10-20T09:00:00+09:00', 'next_1')]},
}


def entry(fid, status, url, dtype='gtfs'):
    return {'id': fid, 'data_type': dtype, 'status': status, 'provider': f'P {fid}', 'name': '',
            'urls.direct_download': url, 'urls.latest': mirror(fid)}


CATALOG = [
    entry('jbda-town-a-bus', 'active', direct('town-a', 'bus')),
    entry('jbda-cityb-loop', 'active', direct('cityb', 'loop', '?uid=abc')),
    entry('jbda-townc-demand', 'active', direct('townc', 'demand', '')),
    entry('jbda-oldtown-line', 'active', direct('oldtown', 'line')),
    entry('jbda-gone-x', 'inactive', direct('gone', 'x')),
    entry('jbda-kita-mini', 'active', 'https://example.jp/kita/mini.zip'),
    entry('jbda-minami-bus', 'future', direct('minami', 'bus', '?rid=next')),
    entry('jbda-town-a-bus-rt', 'active', 'https://example.jp/rt', 'gtfs_rt'),
    entry('mdb-1', 'active', 'https://example.com/gtfs.zip'),
]

FILES = {
    mirror('jbda-town-a-bus'): (make_zip(CAL_A, 'gtfs/', zipfile.ZIP_STORED), 'Thu, 01 Oct 2026 01:19:42 GMT'),
    mirror('jbda-cityb-loop'): (make_zip(CAL_C), 'Fri, 03 Apr 2026 03:00:00 GMT'),
    mirror('jbda-townc-demand'): (make_zip(CAL_OLD2), ''),
    mirror('jbda-oldtown-line'): (make_zip(CAL_OLD), ''),
    mirror('jbda-gone-x'): (make_zip(CAL_OLD), ''),
    mirror('jbda-kita-mini'): (make_zip(CAL_A2), ''),
    mirror('jbda-minami-bus'): (make_zip(CAL_NEXT), ''),
    mc.file_url('town-a', 'bus', 'current'): (make_zip(CAL_A), ''),
    mc.file_url('cityb', 'loop', 'current'): (make_zip(CAL_C), ''),
    mc.file_url('cityb', 'loop', 'next_1'): (make_zip(CAL_NEXT), ''),
    mc.file_url('townc', 'demand', 'current'): (make_zip(CAL_D), ''),
    mc.file_url('townc', 'demand', 'prev_1'): (make_zip(CAL_OLD2), ''),
    mc.file_url('kita', 'mini', 'current'): (make_zip(CAL_E), ''),
    mc.file_url('minami', 'bus', 'current'): (make_zip(CAL_C), ''),
    mc.file_url('minami', 'bus', 'next_1'): (make_zip(CAL_NEXT), ''),
}


class Fake:
    def __init__(self):
        self.urls = []

    def read(self, url):
        self.urls.append(url)
        if url not in FILES:
            return {'result': 'http_404', 'modified': '', 'sig': None, 'first_date': None, 'last_date': None,
                    'feed_end_date': None}
        data, modified = FILES[url]
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            out = mc.zip_facts(z)
        out.update({'result': 'ok', 'modified': modified})
        return out


def fetch(org, fid):
    return BODIES.get((org, fid))


class Parts(unittest.TestCase):
    def test_url_form(self):
        self.assertEqual(mc.url_form(direct('town-a', 'bus')), ('town-a', 'bus', 'rid=current'))
        self.assertEqual(mc.url_form(direct('cityb', 'loop', '?uid=abc')), ('cityb', 'loop', 'uid'))
        self.assertEqual(mc.url_form(direct('a', 'b', '')), ('a', 'b', 'bare'))
        self.assertEqual(mc.url_form(direct('a%20b', 'c', '?rid=next')), ('a b', 'c', 'rid=next'))
        self.assertEqual(mc.url_form('https://example.jp/x.zip'), ('', '', 'other'))
        self.assertEqual(mc.url_form(None), ('', '', 'other'))

    def test_dates(self):
        self.assertEqual(mc.http_day('Thu, 01 Oct 2026 01:19:42 GMT'), dt.date(2026, 10, 1))
        self.assertIsNone(mc.http_day(''))
        self.assertIsNone(mc.http_day('not a date'))
        self.assertEqual(mc.jst_day('2026-10-13T20:00:00Z'), dt.date(2026, 10, 14))   # 05:00 in Japan
        self.assertEqual(mc.jst_day('2026-10-14T18:00:00+09:00'), dt.date(2026, 10, 14))

    def test_signature(self):
        def sig(data):
            with zipfile.ZipFile(io.BytesIO(data)) as z:
                return mc.signature(z)
        a = sig(make_zip(CAL_A))
        self.assertEqual(sig(make_zip(CAL_A, 'gtfs/', zipfile.ZIP_STORED)), a)      # repacked: same files
        files = dict(CAL_A, **{'__MACOSX/._calendar.txt': 'x', 'readme.md': 'x'})
        self.assertEqual(sig(make_zip(files)), a)                                    # junk and non-.txt ignored
        self.assertNotEqual(sig(make_zip(CAL_A2)), a)
        self.assertEqual([n for n, _, _ in a], ['agency.txt', 'calendar.txt'])

    def test_zip_facts(self):
        with zipfile.ZipFile(io.BytesIO(make_zip(CAL_OLD2))) as z:
            f = mc.zip_facts(z)
        self.assertEqual((f['first_date'], f['last_date']), (dt.date(2025, 10, 15), dt.date(2026, 10, 14)))
        with zipfile.ZipFile(io.BytesIO(make_zip({'agency.txt': AGENCY}))) as z:
            f = mc.zip_facts(z)
        self.assertIsNone(f['last_date'])
        self.assertEqual(len(f['sig']), 1)

    def test_locate(self):
        by_key = {(f['organization_id'], f['feed_id']): f for f in FEEDS}
        by_id = {f'jbda-{f["organization_id"]}-{f["feed_id"]}'.lower(): f for f in FEEDS}
        got = {r['id']: mc.locate(r, by_key, by_id) for r in mc.jbda_rows(CATALOG)}
        self.assertEqual(got['jbda-town-a-bus'], ('town-a', 'bus', 'url', 'rid=current'))
        self.assertEqual(got['jbda-kita-mini'], ('kita', 'mini', 'id', 'other'))
        self.assertEqual(got['jbda-gone-x'], ('gone', 'x', 'url_unlisted', 'rid=current'))
        self.assertEqual(len(got), 7)   # the gtfs_rt row and the mdb- row are not repository entries


class Run(unittest.TestCase):
    def setUp(self):
        self.fake = Fake()
        self.rows, self.cov, self.missing = mc.run(CATALOG, FEEDS, AS_OF, self.fake.read, fetch, pause=0,
                                                   log=io.StringIO())
        self.by = {r['id']: r for r in self.rows}

    def test_holds(self):
        self.assertEqual({k: r['holds'] for k, r in self.by.items()},
                         {'jbda-cityb-loop': 'current', 'jbda-gone-x': 'unread', 'jbda-kita-mini': 'other',
                          'jbda-minami-bus': 'next_1', 'jbda-oldtown-line': 'unread', 'jbda-town-a-bus': 'current',
                          'jbda-townc-demand': 'prev_1'})
        self.assertEqual([r['id'] for r in self.rows], sorted(self.by))

    def test_reads(self):
        # The previous file is read only when the mirror differs; the next file only when one is published; an
        # unlisted feed's repository file is never read.
        u = self.fake.urls
        self.assertNotIn(mc.file_url('cityb', 'loop', 'next_1'), u)
        self.assertNotIn(mc.file_url('minami', 'bus', 'prev_1'), u)
        self.assertIn(mc.file_url('townc', 'demand', 'prev_1'), u)
        self.assertNotIn(mc.file_url('townc', 'demand', 'next_1'), u)
        self.assertNotIn(mc.file_url('gone', 'x', 'current'), u)
        self.assertEqual(len(u), 7 + 6 + 1 + 2)   # mirrors, current files, minami next, townc + kita prev

    def test_lag_and_stale(self):
        b = self.by
        # town-a: in force from 10-01 (published 08-31), mirror written 10-01 -> 0. cityb: from 04-01, written 04-03.
        self.assertEqual(b['jbda-town-a-bus']['mirror_lag_days'], 0)
        self.assertEqual(b['jbda-cityb-loop']['mirror_lag_days'], 2)
        # townc: current since max(10-15, published 10-14) = 10-15 -> 9 days; kita: since 04-01 -> 183 + 23 = 206.
        self.assertEqual(b['jbda-townc-demand']['stale_days'], 9)
        self.assertEqual(b['jbda-kita-mini']['stale_days'], 206)
        self.assertEqual(b['jbda-minami-bus']['stale_days'], '')
        self.assertEqual(b['jbda-townc-demand']['mirror_class'], 'expired')
        self.assertEqual(b['jbda-townc-demand']['source_running'], 'yes')
        self.assertEqual(b['jbda-oldtown-line']['source_running'], 'no')
        self.assertEqual(b['jbda-oldtown-line']['source_result'], 'http_404')
        self.assertEqual(b['jbda-gone-x']['source_running'], 'no')
        self.assertEqual(b['jbda-cityb-loop']['next_from'], dt.date(2026, 11, 1))
        self.assertEqual(b['jbda-cityb-loop']['later_files'], 1)
        self.assertEqual(b['jbda-oldtown-line']['later_files'], 0)
        self.assertEqual(b['jbda-gone-x']['later_files'], '')

    def test_coverage(self):
        # In scope: town-a, cityb, townc, vill, kita, minami (oldtown discontinued, closed not open, ended expired).
        self.assertEqual(self.cov, {'in_scope': 6, 'with_entry': 5, 'missing': 1})
        self.assertEqual([(m['organization_id'], m['feed_id']) for m in self.missing], [('vill', 'e')])

    def test_summary_and_predictions(self):
        s = mc.summarise(self.rows, self.cov, AS_OF, 8)
        self.assertEqual(s['holds'], {'current': 2, 'next_1': 1, 'prev_1': 1, 'other': 1, 'unread': 2})
        self.assertEqual(s['holds_active'], {'current': 2, 'next_1': 0, 'prev_1': 1, 'other': 1, 'unread': 1})
        self.assertEqual(s['url_form'], {'rid=current': 3, 'uid': 1, 'bare': 1, 'other': 1, 'rid=next': 1})
        self.assertEqual(s['match_by'], {'url': 5, 'url_unlisted': 1, 'id': 1})
        self.assertEqual((s['source_listed_no'], s['source_discontinued']), (1, 1))
        self.assertEqual((s['mirror_expired'], s['mirror_expired_source_running']), (3, 1))
        self.assertEqual(s['with_later_file'], 2)
        # Lead times: cityb 11-01 - 10-10 = 22, minami 11-01 - 10-20 = 12.
        self.assertEqual(s['later_lead_days'], {'n': 2, 'min': 12, 'q1': 14.5, 'median': 17.0, 'q3': 19.5,
                                                'max': 22})
        self.assertEqual(s['mirror_lag_days']['median'], 1.0)
        self.assertEqual(s['stale_days']['median'], 107.5)
        p = {k: (v['value'], v['held']) for k, v in s['predictions'].items()}
        # M1: active and both read = town-a, cityb, townc, kita; 2 current -> 0.5. M2: minami holds next_1 of the 2
        # entries with a later file. M3: 5 of 6. M4: mirror expired = townc (running), oldtown, gone -> 2 of 3.
        # M5: active = town-a, cityb, townc, oldtown, kita; oldtown discontinued -> 1 of 5.
        self.assertEqual(p, {'M1': (0.5, False), 'M2': ('1 of 2', False), 'M3': (0.8333, False),
                             'M4': (0.6667, False), 'M5': (0.2, False)})

    def test_score_held(self):
        rows = [dict(self.by['jbda-town-a-bus']), dict(self.by['jbda-cityb-loop'])]
        p = mc.score_m(rows, {'in_scope': 10, 'with_entry': 9, 'missing': 1})
        self.assertEqual({k: (v['value'], v['held']) for k, v in p.items()},
                         {'M1': (1.0, True), 'M2': ('0 of 1', True), 'M3': (0.9, True), 'M4': (None, None),
                          'M5': (0.0, True)})
        p = mc.score_m(rows[:1], {'in_scope': 0, 'with_entry': 0, 'missing': 0})
        self.assertEqual((p['M2']['value'], p['M2']['held']), ('0 of 0', None))
        self.assertIsNone(p['M3']['held'])


class Main(unittest.TestCase):
    def test_end_to_end(self):
        with tempfile.TemporaryDirectory() as d:
            cat = os.path.join(d, 'feeds_v2.csv')
            cols = list(CATALOG[0])
            with open(cat, 'w', encoding='utf-8-sig', newline='') as f:
                w = csv.DictWriter(f, fieldnames=cols)
                w.writeheader()
                w.writerows(CATALOG)
            out = os.path.join(d, 'out')
            s = mc.main(['--catalog', cat, '--as-of', '2026-10-24', '--pause', '0', '--min-feeds', '1',
                         '--out', out], read=Fake().read, fetch=fetch, feeds_doc={'code': 200, 'body': FEEDS})
            self.assertEqual((s['entries'], s['catalog_gtfs_rows']), (7, 8))
            day_dir = os.path.join(out, '2026-10-24')
            with open(os.path.join(day_dir, 'mirror.csv'), 'rb') as f:
                raw = f.read()
            self.assertTrue(raw.startswith(b'\xef\xbb\xbf'))
            self.assertIn(b'\r\n', raw)
            with open(os.path.join(day_dir, 'mirror.csv'), encoding='utf-8-sig', newline='') as f:
                got = list(csv.DictReader(f))
            self.assertEqual(list(got[0]), mc.COLUMNS)
            self.assertEqual((got[0]['id'], got[0]['holds'], got[0]['mirror_modified'], got[0]['current_since']),
                             ('jbda-cityb-loop', 'current', '2026-04-03', '2026-04-01'))
            with open(os.path.join(day_dir, 'missing.csv'), encoding='utf-8-sig', newline='') as f:
                miss = list(csv.DictReader(f))
            self.assertEqual([(m['organization_id'], m['feed_name']) for m in miss], [('vill', 'e バス')])
            with open(os.path.join(day_dir, 'summary.json'), encoding='utf-8') as f:
                self.assertEqual(json.load(f)['predictions']['M2']['value'], '1 of 2')
            with open(os.path.join(day_dir, 'summary.md'), encoding='utf-8') as f:
                md = f.read()
            self.assertIn('- mirror holds (all entries): current 2, next_1 1, prev_1 1, other 1, unread 2', md)
            self.assertIn('| jbda-kita-mini | active | other | 2027-09-30 | 2026-04-01 | 2027-03-31 | 206 | yes |', md)
            self.assertIn('Result: 50.0%, did not hold.', md)
            self.assertIn('Result: 1 of 2, did not hold.', md)

    def test_too_few_feeds(self):
        with tempfile.TemporaryDirectory() as d:
            cat = os.path.join(d, 'c.csv')
            with open(cat, 'w', encoding='utf-8') as f:
                f.write('id,data_type\n')
            with self.assertRaises(SystemExit):
                mc.main(['--catalog', cat, '--out', d], read=Fake().read, fetch=fetch, feeds_doc={'body': FEEDS})


if __name__ == '__main__':
    unittest.main()
