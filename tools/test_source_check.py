# Tests for source_check.py on made-up zips served from memory. Every expected value is worked by hand.
# MV2 of Munim, Inc. - Apache-2.0 license. Made with AI agents working in MV2's name.
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
import source_check as sc  # noqa: E402

AS_OF = dt.date(2026, 10, 23)
HEAD = 'service_id,monday,tuesday,wednesday,thursday,friday,saturday,sunday,start_date,end_date\n'
AGENCY = 'agency_id,agency_name,agency_url,agency_timezone\nA,Bus,https://example.org/,America/New_York\n'


def make_zip(files, folder='', method=zipfile.ZIP_DEFLATED):
    b = io.BytesIO()
    with zipfile.ZipFile(b, 'w', method) as z:
        for n, t in files.items():
            z.writestr(folder + n, t)
    return b.getvalue()


def gtfs(start, end):
    return {'agency.txt': AGENCY, 'calendar.txt': HEAD + f'S1,1,1,1,1,1,1,1,{start},{end}\n'}


# Every service runs daily, so the first and last service dates are the calendar range ends.
CAL_A = gtfs('20261001', '20270930')      # runs to 2027-09-30
CAL_C = gtfs('20260401', '20261031')      # runs to 2026-10-31 (still running on AS_OF)
CAL_OLD = gtfs('20251001', '20260930')    # ended 2026-09-30, 23 days before AS_OF
CAL_OLD2 = gtfs('20251015', '20261014')   # ended 2026-10-14, 9 days before AS_OF
CAL_OLD3 = gtfs('20251101', '20261020')   # ended 2026-10-20, a different file that has also ended


def mirror(fid):
    return f'https://files.mobilitydatabase.org/{fid}/latest.zip'


def prod(n):
    return f'https://p{n}.example.org/gtfs.zip'


def entry(fid, status, producer, auth='', dtype='gtfs', latest=True, redirect='', country='US'):
    return {'id': fid, 'data_type': dtype, 'status': status, 'location.country_code': country,
            'provider': f'Bus {fid.split("-")[1]}', 'name': '', 'urls.direct_download': producer,
            'urls.authentication_type': auth, 'urls.latest': mirror(fid) if latest else '', 'redirect.id': redirect}


CATALOG = [
    entry('mdb-1', 'active', prod(1)),                       # copy runs; producer same file -> control same_file
    entry('mdb-2', 'inactive', prod(2)),                     # copy ended; producer runs, differs -> stale copy
    entry('tld-3', 'inactive', prod(3), auth='0.0'),         # copy ended; producer same file, repacked
    entry('tdg-4', 'inactive', prod(4), country='FR'),       # copy ended; producer 404
    entry('mdb-5', 'inactive', prod(5), auth='1'),           # copy ended; producer needs a key
    entry('mdb-6', 'active', prod(6)),                       # copy ended; producer differs and has ended too
    entry('mdb-7', 'inactive', ''),                          # copy ended; no producer URL
    entry('mdb-8', 'inactive', prod(8)),                     # copy ended; producer network error
    entry('mdb-9', 'inactive', prod(9)),                     # copy ended; producer zip without a calendar
    entry('mdb-10', 'active', prod(10)),                     # copy cannot be read
    entry('mdb-11', 'active', prod(11)),                     # copy runs; producer differs and runs
    entry('mdb-12', 'deprecated', prod(12)),                 # not selected
    entry('mdb-13', 'active', prod(13), dtype='gtfs_rt'),    # not GTFS Schedule
    entry('mdb-14', 'future', prod(14), latest=False),       # no copy
    entry('mdb-15', 'inactive', prod(15), redirect='mdb-99'),  # copy ended; producer 404; redirected
]
SELECTED = [r for r in CATALOG if r['data_type'] == 'gtfs' and r['status'] in ('active', 'inactive', 'future')]

FILES = {
    mirror('mdb-1'): make_zip(CAL_A), prod(1): make_zip(CAL_A),
    mirror('mdb-2'): make_zip(CAL_OLD), prod(2): (make_zip(CAL_A), 'Thu, 01 Oct 2026 01:00:00 GMT'),
    mirror('tld-3'): make_zip(CAL_OLD), prod(3): make_zip(CAL_OLD, 'gtfs/', zipfile.ZIP_STORED),
    mirror('tdg-4'): make_zip(CAL_OLD),
    mirror('mdb-5'): make_zip(CAL_OLD), prod(5): make_zip(CAL_A),
    mirror('mdb-6'): make_zip(CAL_OLD2), prod(6): make_zip(CAL_OLD3),
    mirror('mdb-7'): make_zip(CAL_OLD),
    mirror('mdb-8'): make_zip(CAL_OLD), prod(8): 'network_error',
    mirror('mdb-9'): make_zip(CAL_OLD), prod(9): make_zip({'agency.txt': AGENCY}),
    mirror('mdb-11'): make_zip(CAL_C), prod(11): make_zip(CAL_A),
    mirror('mdb-15'): make_zip(CAL_OLD),
}


class Fake:
    def __init__(self):
        self.urls = []

    def read(self, url):
        self.urls.append(url)
        v = FILES.get(url, 'http_404')
        if isinstance(v, str):
            return {'result': v, 'modified': '', 'sig': None, 'first_date': None, 'last_date': None,
                    'feed_end_date': None}
        data, modified = v if isinstance(v, tuple) else (v, '')
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            out = mc.zip_facts(z)
        out.update({'result': 'ok', 'modified': modified})
        return out


class FakeClock:
    def __init__(self):
        self.slept = []

    def now(self):
        return 0.0

    def sleep(self, s):
        self.slept.append(s)


class Parts(unittest.TestCase):
    def test_auth_needed(self):
        got = [sc.auth_needed({'urls.authentication_type': v}) for v in ('', '0', '0.0', ' 0 ', '1', '2.0', 'x')]
        self.assertEqual(got, [False, False, False, False, True, True, True])
        self.assertFalse(sc.auth_needed({}))

    def test_host_gate(self):
        c = FakeClock()
        g = sc.HostGate(1.0, c.now, c.sleep)
        for u in ('https://a.com/x', 'https://a.com/y', 'https://b.org/', 'https://A.com/z'):
            g.wait(u)
        self.assertEqual(c.slept, [1.0, 2.0])   # the second and third file from a.com wait 1 s and 2 s
        c2 = FakeClock()
        sc.HostGate(0, c2.now, c2.sleep).wait('https://a.com/')
        self.assertEqual(c2.slept, [])

    def test_groups(self):
        f = Fake()
        mirrors = [f.read(r['urls.latest']) if r['urls.latest'] else dict(sc.NO_FILE) for r in SELECTED]
        g = sc.assign_groups(SELECTED, mirrors, AS_OF, 10, 1)
        by = {r['id']: x for r, x in zip(SELECTED, g)}
        self.assertEqual(sorted(k for k, v in by.items() if v == 'control'), ['mdb-1', 'mdb-11'])
        self.assertEqual(sorted(k for k, v in by.items() if v == 'expired'),
                         ['mdb-15', 'mdb-2', 'mdb-5', 'mdb-6', 'mdb-7', 'mdb-8', 'mdb-9', 'tdg-4', 'tld-3'])
        self.assertEqual((by['mdb-10'], by['mdb-14']), ('', ''))
        one = sc.assign_groups(SELECTED, mirrors, AS_OF, 1, 7)
        self.assertEqual(one.count('control'), 1)
        self.assertEqual(one, sc.assign_groups(SELECTED, mirrors, AS_OF, 1, 7))   # the same seed, the same sample
        self.assertEqual(sc.assign_groups(SELECTED, mirrors, AS_OF, 0, 7).count('control'), 0)


class Run(unittest.TestCase):
    def setUp(self):
        self.fake = Fake()
        self.rows = sc.run(SELECTED, AS_OF, self.fake.read, control=10, seed=1, workers=2, pause=0, host_pause=0,
                           log=io.StringIO())
        self.by = {r['id']: r for r in self.rows}

    def test_verdicts(self):
        self.assertEqual({k: (r['group'], r['verdict']) for k, r in self.by.items()},
                         {'mdb-1': ('control', 'same_file'), 'mdb-2': ('expired', 'differs_running'),
                          'tld-3': ('expired', 'same_file'), 'tdg-4': ('expired', 'producer_unreadable'),
                          'mdb-5': ('expired', 'auth_required'), 'mdb-6': ('expired', 'differs_ended'),
                          'mdb-7': ('expired', 'no_direct_url'), 'mdb-8': ('expired', 'producer_unreadable'),
                          'mdb-9': ('expired', 'producer_no_dates'), 'mdb-10': ('', 'not_checked'),
                          'mdb-11': ('control', 'differs_running'), 'mdb-14': ('', 'not_checked'),
                          'mdb-15': ('expired', 'producer_unreadable')})
        self.assertEqual([r['id'] for r in self.rows], sorted(self.by))

    def test_reads(self):
        u = self.fake.urls
        # 12 copies (mdb-14 has none) and 9 producer files: not mdb-5 (key), mdb-7 (no URL), mdb-10 (copy unread).
        self.assertEqual(len(u), 12 + 9)
        for n in (5, 7, 10, 12, 13, 14):
            self.assertNotIn(prod(n), u)

    def test_columns(self):
        b = self.by
        r = b['mdb-2']
        self.assertEqual((r['mirror_last'], r['producer_last'], r['producer_modified']),
                         (dt.date(2026, 9, 30), dt.date(2027, 9, 30), dt.date(2026, 10, 1)))
        self.assertEqual((r['days_since_copy_ended'], r['producer_ahead_days'], r['mirror_class'],
                          r['producer_class'], r['producer_host']),
                         (23, 365, 'expired', 'ends_within_1y', 'p2.example.org'))   # 342 days left
        self.assertEqual((b['mdb-6']['days_since_copy_ended'], b['mdb-6']['producer_ahead_days']), (9, 6))
        self.assertEqual(b['tld-3']['producer_ahead_days'], 0)
        self.assertEqual(b['mdb-5']['producer_host'], 'p5.example.org')
        self.assertEqual(b['tdg-4']['producer_result'], 'http_404')
        self.assertEqual(b['mdb-8']['producer_result'], 'network_error')
        self.assertEqual(b['mdb-1']['days_since_copy_ended'], '')     # control rows have no such count
        self.assertEqual(b['mdb-10']['mirror_result'], 'http_404')
        self.assertEqual(b['mdb-14']['mirror_result'], 'no_latest')
        self.assertEqual((b['mdb-15']['redirect'], b['tdg-4']['country'], b['tdg-4']['source']),
                         ('mdb-99', 'FR', 'tdg'))

    def test_summary_and_predictions(self):
        s = sc.summarise(self.rows, AS_OF, control=10, seed=1)
        self.assertEqual(s['groups'], {'expired': 9, 'control': 2, 'control_asked': 10, 'seed': 1})
        self.assertEqual(s['expired_verdicts'], {'same_file': 1, 'differs_running': 1, 'differs_ended': 1,
                                                 'producer_no_dates': 1, 'producer_unreadable': 3,
                                                 'auth_required': 1, 'no_direct_url': 1})
        self.assertEqual(s['control_verdicts']['same_file'], 1)
        self.assertEqual(s['control_verdicts']['differs_running'], 1)
        self.assertEqual(s['expired_verdicts_by_status']['active']['differs_ended'], 1)
        self.assertEqual(sum(s['expired_verdicts_by_status']['inactive'].values()), 8)
        self.assertEqual(sum(s['expired_verdicts_by_source']['mdb'].values()), 7)
        self.assertEqual(s['expired_failures'], {'http_404': 2, 'network_error': 1})
        self.assertEqual(s['control_failures'], {})
        self.assertEqual(s['expired_redirected'], 1)
        self.assertEqual(s['stale']['n'], 1)
        self.assertEqual(s['stale']['days_since_copy_ended']['median'], 23)
        self.assertEqual(s['stale']['producer_ahead_days']['median'], 365)
        self.assertEqual(s['stale']['producer_modified_days_before_as_of']['median'], 22)
        p = {k: (v['value'], v['held']) for k, v in s['predictions'].items()}
        # S1: 7 expired entries with an open URL (not mdb-5, mdb-7); 3 read with dates (mdb-2, tld-3, mdb-6) -> 3/7.
        # S2: 1 stale (mdb-2) of 3. S3: ended at the producer = tld-3 (same), mdb-6 (differs) -> 1/2.
        # S4: control read = mdb-1 (same), mdb-11 (differs) -> 1/2. S5: http_404 2 (tdg-4, mdb-15), network_error 1.
        self.assertEqual(p, {'S1': (0.4286, True), 'S2': (0.3333, False), 'S3': (0.5, False), 'S4': (0.5, False),
                             'S5': ('http_404 2 of 3', True)})

    def test_score_edges(self):
        self.assertEqual({k: v['held'] for k, v in sc.score_s([]).items()},
                         {'S1': None, 'S2': None, 'S3': None, 'S4': None, 'S5': None})
        tie = [dict(self.by['tdg-4']), dict(self.by['mdb-8'])]          # http_404 1, network_error 1: not strictly
        self.assertEqual((sc.score_s(tie)['S5']['value'], sc.score_s(tie)['S5']['held']), ('http_404 1 of 2', False))


class Main(unittest.TestCase):
    def test_end_to_end(self):
        with tempfile.TemporaryDirectory() as d:
            cat = os.path.join(d, 'feeds_v2.csv')
            with open(cat, 'w', encoding='utf-8-sig', newline='') as f:
                w = csv.DictWriter(f, fieldnames=list(CATALOG[0]))
                w.writeheader()
                w.writerows(CATALOG)
            out = os.path.join(d, 'out')
            s = sc.main(['--catalog', cat, '--as-of', '2026-10-23', '--control', '10', '--seed', '1', '--pause', '0',
                         '--host-pause', '0', '--workers', '2', '--out', out], read=Fake().read)
            self.assertEqual(s['entries'], 13)
            # Counted over GTFS Schedule rows, so the gtfs_rt row mdb-13 is not among the 4 active ones.
            self.assertEqual(s['catalog_status'], {'inactive': 8, 'active': 4, 'deprecated': 1, 'future': 1})
            self.assertEqual(s['by_status'], {'inactive': 8, 'active': 4, 'future': 1})
            day_dir = os.path.join(out, '2026-10-23')
            with open(os.path.join(day_dir, 'sources.csv'), 'rb') as f:
                raw = f.read()
            self.assertTrue(raw.startswith(b'\xef\xbb\xbf'))
            self.assertIn(b'\r\n', raw)
            with open(os.path.join(day_dir, 'sources.csv'), encoding='utf-8-sig', newline='') as f:
                got = list(csv.DictReader(f))
            self.assertEqual(list(got[0]), sc.COLUMNS)
            self.assertEqual(len(got), 13)
            row = {r['id']: r for r in got}['mdb-2']
            self.assertEqual((row['mirror_last'], row['producer_last'], row['producer_modified'],
                              row['days_since_copy_ended'], row['producer_ahead_days'], row['verdict']),
                             ('2026-09-30', '2027-09-30', '2026-10-01', '23', '365', 'differs_running'))
            with open(os.path.join(day_dir, 'summary.json'), encoding='utf-8') as f:
                self.assertEqual(json.load(f)['predictions']['S5']['value'], 'http_404 2 of 3')
            with open(os.path.join(day_dir, 'summary.md'), encoding='utf-8') as f:
                md = f.read()
            self.assertIn('- expired group (9): same_file 1, differs_running 1, differs_ended 1, producer_no_dates 1, '
                          'producer_unreadable 3, auth_required 1, no_direct_url 1', md)
            self.assertIn('- control group (2): same_file 1, differs_running 1, differs_ended 0', md)
            self.assertIn('- producer URLs that could not be read, expired group: http_404 2, network_error 1', md)
            self.assertIn('- producer URLs that could not be read, control group: none', md)
            self.assertIn('| mdb-2 | inactive | US | Bus 2 | 2026-09-30 | 2027-09-30 | 2026-10-01 | 23 |', md)
            self.assertIn('Result: 42.9%, held.', md)
            self.assertIn('Result: http_404 2 of 3, held.', md)


if __name__ == '__main__':
    unittest.main()
