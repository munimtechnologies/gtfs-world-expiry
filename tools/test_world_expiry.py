# Tests for world_expiry.py on made-up zips served from memory (no network). Every expected value is worked by hand.
# MV2 of Munim, Inc. - Apache-2.0 license. Made with AI agents working in MV2's name.
import csv
import datetime as dt
import io
import json
import os
import sys
import tempfile
import unittest
import urllib.error
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import world_expiry as wx  # noqa: E402

D = dt.date
AS_OF = D(2026, 10, 22)


def make_zip(files):
    b = io.BytesIO()
    with zipfile.ZipFile(b, 'w', zipfile.ZIP_DEFLATED) as z:
        for name, text in files.items():
            z.writestr(name, text)
    return b.getvalue()


def opener_for(data, block=64):
    """An opener that serves `data` through a RangeFile with a small block, as the server's tail request would."""
    def opener(url):
        start = max(0, len(data) - block)
        return wx.RangeFile(len(data), lambda lo, hi: data[lo:hi + 1], start, data[start:], block=block,
                            max_ahead=4 * block)
    return opener


# Feed A. 2026-01-05 is a Monday, 2026-01-18 a Sunday.
# WK runs Mon-Fri 01-05..01-18: first 01-05; last: 01-18 Sun, 01-17 Sat not flagged, 01-16 Fri removed -> 01-15 Thu.
# SA is Saturday-only inside Mon 01-05..Fri 01-09, so it never runs. X is added on 01-25 only.
# Services WK, SA, X = 3; first 01-05; last max(01-15, 01-25) = 2026-01-25.
# Days from 2026-01-25 to 2026-10-22: 6 (rest of Jan) + 28 + 31 + 30 + 31 + 30 + 31 + 31 + 30 + 22 = 270 -> -270.
FEED_A = make_zip({
    'calendar.txt': 'service_id,monday,tuesday,wednesday,thursday,friday,saturday,sunday,start_date,end_date\n'
                    'WK,1,1,1,1,1,0,0,20260105,20260118\nSA,0,0,0,0,0,1,0,20260105,20260109\n',
    'calendar_dates.txt': 'service_id,date,exception_type\nWK,20260116,2\nX,20260125,1\nWK,20250101,2\n',
    'feed_info.txt': 'feed_publisher_name,feed_publisher_url,feed_lang,feed_start_date,feed_end_date\n'
                     'P,https://example.org,en,20260105,20260131\n',
    'stops.txt': 'stop_id,stop_name,stop_lat,stop_lon\n' + ''.join(f's{i},Stop {i},35.0,139.0\n' for i in range(200)),
})
# Feed B: calendar_dates only, in a folder, with a BOM and spaces in the header, CRLF, and a macOS shadow file.
# B1 runs 2026-11-01 and 2027-03-31; B2's removal is not a calendar service and is ignored. Services 1.
# Days from 2026-10-22 to 2027-03-31: 9 + 30 + 31 + 31 + 28 + 31 = 160 -> ends_within_1y, end day 03-31.
FEED_B = make_zip({
    'gtfs/calendar_dates.txt': '﻿ service_id , date , exception_type\r\nB1,20261101,1\r\nB1,20270331,1\r\n'
                               'B2,20270101,2\r\n',
    '__MACOSX/gtfs/._calendar_dates.txt': 'junk',
    'gtfs/stops.txt': 'stop_id\n1\n',
})
FEED_C = make_zip({'stops.txt': 'stop_id\n1\n'})


def cat_row(fid, url, country='JP'):
    return {'id': fid, 'urls.latest': url, 'location.country_code': country, 'location.subdivision_name': 'S',
            'provider': 'Prov', 'name': 'Name'}


class TestRangeFile(unittest.TestCase):
    def test_reads_and_requests(self):
        data = bytes(range(256)) * 10
        calls = []

        def fetch(lo, hi):
            calls.append((lo, hi))
            return data[lo:hi + 1]
        f = wx.RangeFile(len(data), fetch, len(data) - 64, data[-64:], block=64, max_ahead=256)
        f.seek(10)
        self.assertEqual(f.read(5), data[10:15])          # outside the tail buffer: fetch 10..73
        self.assertEqual(f.read(100), data[15:115])       # not inside 10..73: fetch 15..114
        self.assertEqual(f.read(10), data[115:125])       # continues the buffer: ahead doubles to 128, 115..242
        f.seek(-10, 2)
        self.assertEqual(f.read(), data[2550:2560])       # near the end: the last 64 bytes, 2496..2559
        self.assertEqual(calls, [(10, 73), (15, 114), (115, 242), (2496, 2559)])
        self.assertEqual((f.requests, f.bytes_read), (4, 64 + 64 + 100 + 128 + 64))
        self.assertEqual(f.read(3), b'')

    def test_negative_seek(self):
        f = wx.RangeFile(10, lambda lo, hi: b'', 0, b'0123456789')
        with self.assertRaises(OSError):
            f.seek(-11, 2)

    def test_zipfile_through_rangefile(self):
        f = opener_for(FEED_A)('x')
        with zipfile.ZipFile(f) as z:
            self.assertIn('calendar.txt', z.namelist())
            self.assertTrue(z.read('stops.txt').startswith(b'stop_id,'))
        self.assertGreater(f.requests, 1)


class TestDates(unittest.TestCase):
    WD = (True, True, True, True, True, False, False)

    def test_gdate(self):
        self.assertEqual(wx.gdate(' 20260105 '), D(2026, 1, 5))
        self.assertIsNone(wx.gdate('2026-01-05'))
        self.assertIsNone(wx.gdate('20260230'))

    def test_first_last_active(self):
        self.assertEqual(wx.first_active(D(2026, 1, 3), D(2026, 1, 18), self.WD), D(2026, 1, 5))  # Sat 01-03
        self.assertEqual(wx.last_active(D(2026, 1, 5), D(2026, 1, 18), self.WD), (D(2026, 1, 16), False))
        self.assertEqual(wx.last_active(D(2026, 1, 5), D(2026, 1, 18), self.WD, {D(2026, 1, 16)}),
                         (D(2026, 1, 15), False))
        sat = (False,) * 5 + (True, False)
        self.assertIsNone(wx.first_active(D(2026, 1, 5), D(2026, 1, 9), sat))
        self.assertEqual(wx.last_active(D(2026, 1, 5), D(2026, 1, 9), sat), (None, False))

    def test_tail_cut(self):
        # Every day 01-29..03-31 (3 + 28 + 31 = 62 days) removed: the 62-day window finds nothing -> cut.
        removed = {D(2026, 1, 29) + dt.timedelta(days=i) for i in range(62)}
        self.assertEqual(max(removed), D(2026, 3, 31))
        self.assertEqual(wx.last_active(D(2026, 1, 1), D(2026, 3, 31), (True,) * 7, removed), (None, True))
        removed.discard(D(2026, 1, 29))
        self.assertEqual(wx.last_active(D(2026, 1, 1), D(2026, 3, 31), (True,) * 7, removed),
                         (D(2026, 1, 29), False))

    def test_classify(self):
        self.assertEqual(wx.classify(D(2026, 10, 21), AS_OF), (-1, 'expired'))
        self.assertEqual(wx.classify(D(2026, 10, 22), AS_OF), (0, 'ends_within_30d'))
        self.assertEqual(wx.classify(D(2025, 10, 22), AS_OF), (-365, 'expired'))
        self.assertEqual(wx.classify(D(2025, 10, 21), AS_OF), (-366, 'expired_over_1y'))
        self.assertEqual(wx.classify(D(2026, 11, 20), AS_OF), (29, 'ends_within_30d'))
        self.assertEqual(wx.classify(D(2026, 11, 21), AS_OF), (30, 'ends_within_1y'))
        self.assertEqual(wx.classify(D(2027, 10, 21), AS_OF), (364, 'ends_within_1y'))
        self.assertEqual(wx.classify(D(2027, 10, 22), AS_OF), (365, 'ends_1_2y'))
        self.assertEqual(wx.classify(None, AS_OF), (None, ''))

    def test_find_members(self):
        m = wx.find_members(['a/b/calendar.txt', 'a/calendar.txt', '__MACOSX/calendar.txt', 'a/', 'FEED_INFO.TXT'])
        self.assertEqual(m, {'calendar.txt': 'a/calendar.txt', 'feed_info.txt': 'FEED_INFO.TXT'})


class TestProcessFeed(unittest.TestCase):
    def test_feed_a(self):
        r = wx.process_feed(cat_row('mdb-1', 'a'), AS_OF, opener_for(FEED_A))
        self.assertEqual(r['result'], 'ok', r['error'])
        self.assertEqual((r['first_date'], r['last_date'], r['services'], r['tail_cut'], r['feed_end_date']),
                         (D(2026, 1, 5), D(2026, 1, 25), 3, 0, D(2026, 1, 31)))
        self.assertEqual((r['days_left'], r['class'], r['end_md'], r['source'], r['ranged']),
                         (-270, 'expired', '01-25', 'mdb', 'yes'))
        self.assertEqual(r['zip_bytes'], len(FEED_A))
        self.assertGreater(r['requests'], 1)

    def test_feed_b(self):
        r = wx.process_feed(cat_row('jbda-x-y', 'b'), AS_OF, opener_for(FEED_B))
        self.assertEqual(r['result'], 'ok', r['error'])
        self.assertEqual((r['first_date'], r['last_date'], r['services'], r['feed_end_date']),
                         (D(2026, 11, 1), D(2027, 3, 31), 1, None))
        self.assertEqual((r['days_left'], r['class'], r['end_md'], r['source']), (160, 'ends_within_1y', '03-31', 'jbda'))

    def test_failures(self):
        self.assertEqual(wx.process_feed(cat_row('c', 'c'), AS_OF, opener_for(FEED_C))['result'], 'no_calendar')
        self.assertEqual(wx.process_feed(cat_row('d', 'd'), AS_OF, opener_for(b'not a zip at all'))['result'],
                         'bad_zip')
        self.assertEqual(wx.process_feed(cat_row('f', ''), AS_OF, opener_for(FEED_A))['result'], 'no_latest')

        def not_found(url):
            raise urllib.error.HTTPError(url, 404, 'Not Found', {}, None)
        r = wx.process_feed(cat_row('e', 'e'), AS_OF, not_found)
        self.assertEqual((r['result'], r['requests']), ('http_404', 0))

        def too_big(url):
            raise wx.Skip('too_big')
        self.assertEqual(wx.process_feed(cat_row('g', 'g'), AS_OF, too_big)['result'], 'too_big')


def fr(country, source, result='ok', cls='', md=''):
    return {'country': country, 'source': source, 'result': result, 'class': cls, 'end_md': md, 'ranged': 'yes',
            'bytes_read': 10, 'zip_bytes': 100}


# 11 feeds, 10 read. Expired: JP 1, US 1, FR 2 (both over a year) = 4 of 10 = 0.4 (W1 holds, inclusive).
# By source: tfs (FR) 2 of 3 expired, mdb (US, DE) 1 of 3; Fisher(2,1,1,2): n1=n2=3, k=3, C(6,3)=20;
#   x=2: C(3,2)C(3,1)=9, x=3: 1 -> 10/20 = 0.5 (W2 fails). JP 1/4 = 0.25 (W3 fails).
# Ending within a year: JP 03-31, 03-31, 11-15; US 12-31; FR 12-31 -> n 5; 03-31 and 12-31 tie at 2, 03-31 sorts
#   first -> W4 fails with '03-31 0.4'. JP 03-31 share 2/3 = 0.6667 (W5 holds). US 1/2 = 0.5 (W6 fails).
ROWS = [fr('JP', 'jbda', cls='ends_within_1y', md='03-31'), fr('JP', 'jbda', cls='ends_within_1y', md='03-31'),
        fr('JP', 'jbda', cls='ends_within_30d', md='11-15'), fr('JP', 'jbda', cls='expired', md='01-31'),
        fr('US', 'mdb', cls='expired', md='09-30'), fr('US', 'mdb', cls='ends_within_1y', md='12-31'),
        fr('US', 'mdb', result='http_404'),
        fr('FR', 'tfs', cls='expired_over_1y', md='06-30'), fr('FR', 'tfs', cls='expired_over_1y', md='06-30'),
        fr('FR', 'tfs', cls='ends_within_1y', md='12-31'),
        fr('DE', 'mdb', cls='ends_1_2y', md='06-30')]


class TestSummary(unittest.TestCase):
    def setUp(self):
        self.s = wx.summarise(ROWS, AS_OF, {'active': 11}, predictions=True)

    def test_overall(self):
        self.assertEqual(self.s['overall'], {'feeds': 11, 'ok': 10, 'expired': 4, 'expired_over_1y': 2,
                                             'ends_within_30d': 1, 'ends_within_1y': 4, 'ends_1_2y': 1,
                                             'ends_after_2y': 0, 'expired_share': 0.4})
        self.assertEqual(self.s['results'], {'ok': 10, 'http_404': 1})

    def test_groups(self):
        src = self.s['by_source']
        self.assertEqual((src['tfs']['ok'], src['tfs']['expired'], src['tfs']['expired_over_1y']), (3, 2, 2))
        self.assertEqual((src['mdb']['feeds'], src['mdb']['ok'], src['mdb']['expired']), (4, 3, 1))
        self.assertEqual(self.s['by_country']['JP']['expired_share'], 0.25)
        self.assertEqual(self.s['by_country']['US']['expired_share'], 0.5)

    def test_end_days(self):
        self.assertEqual(self.s['end_days']['all'], {'n': 5, 'top': [['03-31', 2, 0.4], ['12-31', 2, 0.4],
                                                                      ['11-15', 1, 0.2]]})
        self.assertEqual(self.s['end_days']['JP'], {'n': 3, 'top': [['03-31', 2, 0.6667], ['11-15', 1, 0.3333]]})

    def test_predictions(self):
        p = self.s['predictions']
        got = {k: (v['value'], v['held']) for k, v in p.items()}
        self.assertEqual(got, {'W1': (0.4, True), 'W2': (0.5, False), 'W3': (0.25, False), 'W4': ('03-31 0.4', False),
                               'W5': (0.6667, True), 'W6': (0.5, False)})

    def test_fisher(self):
        self.assertEqual(wx.fisher_greater(2, 1, 1, 2), 0.5)
        self.assertEqual(wx.fisher_greater(3, 0, 0, 3), 0.05)
        self.assertIsNone(wx.fisher_greater(0, 0, 1, 1))

    def test_report(self):
        md = wx.report(self.s)
        self.assertIn('| all | 11 | 10 | 4 | 40.0% | 2 | 1 | 4 | 1 |', md)
        self.assertIn('4 other countries have fewer than 10 feeds read', md)
        self.assertIn('- JP (3 feeds): 03-31 2 (66.7%), 11-15 1 (33.3%)', md)
        self.assertIn('Result: p = 0.5, did not hold.', md)
        self.assertIn('Result: 03-31 0.4, did not hold.', md)
        self.assertIn('Result: 40.0%, held.', md)


class TestCatalogRunWrite(unittest.TestCase):
    def test_load_catalog(self):
        cols = ['id', 'data_type', 'status', 'urls.latest', 'location.country_code', 'provider', 'name']
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, 'feeds_v2.csv')
            with open(path, 'w', encoding='utf-8', newline='') as f:
                w = csv.writer(f)
                w.writerow(cols)
                w.writerow(['mdb-1', 'gtfs', 'active', 'a', 'US', 'P', 'N'])
                w.writerow(['mdb-2', 'gtfs', 'inactive', 'b', 'US', 'P', 'N'])
                w.writerow(['mdb-3', 'gtfs_rt', 'active', '', 'US', 'P', 'N'])
                w.writerow(['mdb-4', 'gtfs', '', 'c', 'US', 'P', 'N'])
            rows, status = wx.load_catalog(path)
        self.assertEqual([r['id'] for r in rows], ['mdb-1'])
        self.assertEqual(status, {'active': 1, 'inactive': 1, '(blank)': 1})

    def test_run_and_write(self):
        zips = {'a': FEED_A, 'b': FEED_B}

        def opener(url):
            return opener_for(zips[url])(url)
        cat = [cat_row('mdb-1', 'a', 'US'), cat_row('jbda-2', 'b'), cat_row('tfs-3', '', 'FR')]
        log = io.StringIO()
        rows = wx.run(cat, AS_OF, workers=2, pause=0, opener=opener, log=log)
        self.assertEqual([(r['id'], r['result']) for r in rows],
                         [('mdb-1', 'ok'), ('jbda-2', 'ok'), ('tfs-3', 'no_latest')])
        self.assertIn('3/3 feeds', log.getvalue())
        s = wx.summarise(rows, AS_OF, predictions=True)
        with tempfile.TemporaryDirectory() as tmp:
            wx.write_outputs(rows, s, tmp)
            with open(os.path.join(tmp, 'feeds.csv'), encoding='utf-8-sig', newline='') as f:
                out = list(csv.DictReader(f))
            self.assertEqual(list(out[0].keys()), wx.FEED_COLUMNS)
            self.assertEqual([r['id'] for r in out], ['jbda-2', 'mdb-1', 'tfs-3'])
            self.assertEqual((out[1]['last_date'], out[1]['days_left'], out[1]['class']),
                             ('2026-01-25', '-270', 'expired'))
            self.assertEqual(out[2]['last_date'], '')
            with open(os.path.join(tmp, 'by_country.csv'), encoding='utf-8-sig', newline='') as f:
                bc = list(csv.reader(f))
            self.assertEqual(bc[0], ['country'] + wx.COUNT_KEYS)
            with open(os.path.join(tmp, 'summary.json'), encoding='utf-8') as f:
                self.assertEqual(json.load(f)['overall']['ok'], 2)
            with open(os.path.join(tmp, 'summary.md'), encoding='utf-8') as f:
                self.assertIn('as of 2026-10-22', f.read())


if __name__ == '__main__':
    unittest.main()
