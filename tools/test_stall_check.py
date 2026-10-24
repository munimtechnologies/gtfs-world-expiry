# Tests for stall_check.py on made-up sources.csv rows. Every expected value is worked by hand.
# MV2 of Munim, Inc. - Apache-2.0 license. Made with AI agents working in MV2's name.
import csv
import datetime as dt
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mirror_check as mc  # noqa: E402
import source_check as sc  # noqa: E402
import stall_check as st  # noqa: E402

AS_OF = dt.date(2026, 10, 30)


def row(fid, group, verdict, mm, ml, pm='', pl='', country='', result='ok', presult=''):
    r = {c: '' for c in sc.COLUMNS}
    r.update({'id': fid, 'group': group, 'verdict': verdict, 'mirror_modified': mm, 'mirror_last': ml,
              'producer_modified': pm, 'producer_last': pl, 'country': country,
              'provider': 'Bus ' + fid.split('-')[1], 'mirror_result': result,
              'producer_result': presult or ('ok' if verdict in sc.READ else '')})
    return r


BEFORE = [
    row('mdb-1', 'expired', 'differs_running', '2026-05-13', '2026-07-07', country='ES'),
    row('mdb-2', 'expired', 'differs_running', '2026-04-19', '2026-08-21'),
    row('mdb-3', 'expired', 'differs_running', '2025-05-08', '2025-08-23'),
    row('mdb-4', 'expired', 'differs_running', '2026-03-11', '2026-07-07'),
    row('mdb-5', 'expired', 'same_file', '2026-01-01', '2026-03-31'),            # not stale: ignored
]

AFTER = [
    # still stale: the same copy, the producer's file still differs and runs
    row('mdb-1', 'expired', 'differs_running', '2026-05-13', '2026-07-07', '2026-10-07', '2026-11-19', 'ES'),
    # renewed: a new copy (stored 10-28) that runs, the same file as the producer's
    row('mdb-2', 'control', 'same_file', '2026-10-28', '2026-12-11', '2026-08-18', '2026-12-11'),
    # no new copy, producer now unreadable; mdb-4 is gone from the catalog
    row('mdb-3', 'expired', 'producer_unreadable', '2025-05-08', '2025-08-23', presult='http_404'),
    row('mdb-5', 'expired', 'same_file', '2026-01-01', '2026-03-31', '2026-01-01', '2026-03-31'),
    # stalled: producer file up since 10-15 (15 days), copy stored 05-14 (in the window)
    row('mdb-10', 'control', 'differs_running', '2026-05-14', '2026-12-31', '2026-10-15', '2027-03-31', 'US'),
    # producer file 1 day old: not stalled
    row('mdb-11', 'control', 'differs_running', '2026-05-20', '2027-01-31', '2026-10-29', '2027-03-31'),
    # no producer Last-Modified: not stalled
    row('mdb-12', 'control', 'differs_running', '2026-10-28', '2027-03-31', '', '2027-04-30'),
    row('mdb-13', 'control', 'same_file', '2026-05-01', '2027-03-31', '2026-05-01', '2027-03-31'),
    row('mdb-14', 'control', 'same_file', '2026-09-01', '2027-06-30', '2026-09-01', '2027-06-30'),
    # producer unreadable: not among the live entries read
    row('mdb-15', 'control', 'producer_unreadable', '2026-09-01', '2027-01-01', presult='http_502'),
    # stalled: producer file up since 09-01 (59 days), copy stored 06-10 (in the window)
    row('mdb-16', 'control', 'differs_running', '2026-06-10', '2026-11-30', '2026-09-01', '2027-02-28', 'FI'),
    # copy runs, producer file differs and has ended: read, not stalled
    row('mdb-17', 'control', 'differs_ended', '2026-08-01', '2026-11-15', '2026-08-01', '2026-10-01'),
    # a stale copy that was not stale before
    row('mdb-18', 'expired', 'differs_running', '2026-06-01', '2026-09-30', '2026-10-01', '2027-03-31'),
    # edges: copy runs to the as-of date itself, producer file exactly 3 days old -> stalled (not in the window)
    row('mdb-20', 'control', 'differs_running', '2026-10-01', '2026-10-30', '2026-10-27', '2027-01-01'),
    # producer Last-Modified on the day the copy was stored: not stalled
    row('mdb-21', 'control', 'differs_running', '2026-10-10', '2027-01-01', '2026-10-10', '2027-02-01'),
]


class Parts(unittest.TestCase):
    def test_new_copy_and_fate(self):
        b = BEFORE[0]
        self.assertFalse(st.new_copy(b, dict(b, mirror_modified='')))               # no header, same last day
        self.assertFalse(st.new_copy(b, dict(b, mirror_modified='2026-05-12')))     # earlier is not newer
        self.assertTrue(st.new_copy(b, dict(b, mirror_modified='2026-05-14')))
        self.assertTrue(st.new_copy(b, dict(b, mirror_modified='', mirror_last='2026-12-31')))
        self.assertEqual(st.fate(b, None), 'gone')
        self.assertEqual(st.fate(b, dict(b, mirror_result='http_404')), 'gone')
        self.assertEqual(st.fate(b, dict(b)), 'still_stale')
        self.assertEqual(st.fate(b, dict(b, verdict='same_file')), 'no_new_copy_other')

    def test_stalled(self):
        by = {r['id']: r for r in AFTER}
        got = {k: st.stalled(r, AS_OF) for k, r in by.items()}
        self.assertEqual(sorted(k for k, v in got.items() if v), ['mdb-10', 'mdb-16', 'mdb-20'])
        self.assertFalse(st.stalled(by['mdb-20'], AS_OF, min_days=4))
        live = sorted(k for k, r in by.items() if st.live_read(r, AS_OF))
        self.assertEqual(live, ['mdb-10', 'mdb-11', 'mdb-12', 'mdb-13', 'mdb-14', 'mdb-16', 'mdb-17', 'mdb-2',
                                'mdb-20', 'mdb-21'])
        self.assertEqual([st.in_window(by[k]) for k in ('mdb-10', 'mdb-16', 'mdb-20', 'mdb-13', 'mdb-14')],
                         [True, True, False, True, False])

    def test_fisher(self):
        self.assertAlmostEqual(st.fisher_greater(2, 0, 1, 5), 3 / 28)    # C(3,2) C(5,0) / C(8,2)
        self.assertAlmostEqual(st.fisher_greater(1, 1, 0, 2), 0.5)       # C(1,1) C(3,1) / C(4,2)
        self.assertAlmostEqual(st.fisher_greater(0, 2, 2, 2), 1.0)       # a = 0: every table counts


class Analyse(unittest.TestCase):
    def setUp(self):
        self.rows, self.s = st.analyse(BEFORE, AFTER, AS_OF)

    def test_rows(self):
        self.assertEqual([(r['kind'], r['id'], r['fate']) for r in self.rows],
                         [('stale_before', 'mdb-1', 'still_stale'), ('stale_before', 'mdb-2', 'renewed'),
                          ('stale_before', 'mdb-3', 'no_new_copy_other'), ('stale_before', 'mdb-4', 'gone'),
                          ('stale_new', 'mdb-18', ''), ('stalled_live', 'mdb-10', ''),
                          ('stalled_live', 'mdb-16', ''), ('stalled_live', 'mdb-20', '')])
        by = {(r['kind'], r['id']): r for r in self.rows}
        self.assertEqual([by[('stalled_live', k)]['days_waiting'] for k in ('mdb-10', 'mdb-16', 'mdb-20')],
                         [15, 59, 3])
        gone = by[('stale_before', 'mdb-4')]
        self.assertEqual((gone['mirror_modified_before'], gone['mirror_modified'], gone['verdict'],
                          gone['in_window'], gone['days_waiting']), ('2026-03-11', '', '', 0, ''))
        ren = by[('stale_before', 'mdb-2')]
        self.assertEqual((ren['mirror_modified_before'], ren['mirror_modified'], ren['in_window']),
                         ('2026-04-19', '2026-10-28', 0))
        self.assertEqual(by[('stale_before', 'mdb-1')]['in_window'], 1)

    def test_summary(self):
        s = self.s
        self.assertEqual(s['stale_before'], {'n': 4, 'fates': {'still_stale': 1, 'no_new_copy_other': 1,
                                                               'renewed': 1, 'gone': 1}})
        self.assertEqual((s['live_read'], s['stalled']), (10, 3))
        self.assertEqual(s['stalled_days_waiting'], {'n': 3, 'min': 3, 'q1': 9.0, 'median': 15, 'q3': 37.0,
                                                     'max': 59})
        self.assertEqual(s['stalled_by_country'], {'US': 1, 'FI': 1, '': 1})
        self.assertEqual(s['window_counts'], {'stalled_in_window': 2, 'stalled': 3, 'others_in_window': 2,
                                              'others': 7})
        self.assertEqual(s['stale_after'], {'n': 2, 'new': 1})
        p = {k: (v['value'], v['held']) for k, v in s['predictions'].items()}
        # T1: 3 still present (mdb-4 gone), 2 with no new copy -> 2/3. T2: 3 stalled of 10 live read.
        # T3: expired read = mdb-1, mdb-5, mdb-18 -> S2 2/3 (missed); ended = mdb-5, same -> S3 1.0 (held);
        # control read = 10, same file = mdb-2, mdb-13, mdb-14 -> S4 0.3 (missed). T4: only 3 stalled.
        self.assertEqual(p, {'T1': (0.6667, False), 'T2': (0.3, False),
                             'T3': ('S2 did not hold, S3 held, S4 did not hold', False), 'T4': (None, None)})

    def test_t4_tested(self):
        stall = [row(f'mdb-{i}', 'control', 'differs_running', '2026-05-01', '2027-01-01', '2026-10-01')
                 for i in range(5)]
        other = [row(f'mdb-{i}', 'control', 'same_file', '2026-09-01', '2027-01-01', '2026-09-01')
                 for i in range(5, 10)]
        _, s = st.analyse([], stall + other, AS_OF)
        p = s['predictions']
        # 5 of 5 stalled in the window, 0 of 5 others: p = C(5,5) C(5,0) / C(10,5) = 1/252.
        self.assertEqual((p['T4']['value'], p['T4']['held']), (0.003968, True))
        self.assertEqual((p['T1']['value'], p['T1']['held']), (None, None))
        self.assertEqual((p['T2']['value'], p['T2']['held']), (0.5, False))


class Main(unittest.TestCase):
    def test_end_to_end(self):
        with tempfile.TemporaryDirectory() as d:
            before, after = os.path.join(d, 'before.csv'), os.path.join(d, 'after.csv')
            mc.write_csv(before, BEFORE, sc.COLUMNS)
            mc.write_csv(after, AFTER, sc.COLUMNS)
            out = os.path.join(d, 'out')
            s = st.main(['--before', before, '--after', after, '--as-of', '2026-10-30', '--out', out])
            self.assertEqual(s['predictions']['T2']['value'], 0.3)
            day_dir = os.path.join(out, '2026-10-30')
            with open(os.path.join(day_dir, 'stalls.csv'), 'rb') as f:
                raw = f.read()
            self.assertTrue(raw.startswith(b'\xef\xbb\xbf'))
            self.assertIn(b'\r\n', raw)
            with open(os.path.join(day_dir, 'stalls.csv'), encoding='utf-8-sig', newline='') as f:
                got = list(csv.DictReader(f))
            self.assertEqual(list(got[0]), st.COLUMNS)
            self.assertEqual(len(got), 8)
            r = {(x['kind'], x['id']): x for x in got}[('stalled_live', 'mdb-16')]
            self.assertEqual((r['mirror_modified'], r['producer_modified'], r['days_waiting'], r['in_window'],
                              r['country']), ('2026-06-10', '2026-09-01', '59', '1', 'FI'))
            with open(os.path.join(day_dir, 'summary.json'), encoding='utf-8') as f:
                self.assertEqual(json.load(f)['stale_after'], {'n': 2, 'new': 1})
            with open(os.path.join(day_dir, 'summary.md'), encoding='utf-8') as f:
                md = f.read()
            self.assertIn('- earlier stale copies: 4; still_stale 1, no_new_copy_other 1, renewed 1, gone 1', md)
            self.assertIn('- entries whose copy still runs and whose producer file was read: 10; stalled downloads: '
                          '3; days the producer file had been up: n 3, median 15 days, quartiles 9.0–37.0, '
                          'range 3–59', md)
            self.assertIn('- stalled downloads by country: US 1, FI 1, ? 1', md)
            self.assertIn('- copy stored 2026-04-19 to 2026-06-18: stalled 2 of 3, other live entries read 2 of 7', md)
            self.assertIn('- stale copies in this run: 2, of which 1 were not stale in the earlier check', md)
            self.assertIn('Result: 66.7%, did not hold.', md)
            self.assertIn('Result: 30.0%, did not hold.', md)
            self.assertIn('Result: S2 did not hold, S3 held, S4 did not hold, did not hold.', md)
            self.assertIn('Result: none, not tested.', md)
            self.assertIn('| mdb-20 | stalled_live |  |  | Bus 20 |  | 2026-10-01 | 2026-10-30 | 2026-10-27 | '
                          '2027-01-01 | 3 |', md)


if __name__ == '__main__':
    unittest.main()
