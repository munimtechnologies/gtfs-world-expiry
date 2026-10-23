# Tests for world_diff.py on two small made-up feeds.csv files. Every expected value is worked by hand.
# MV2 of Munim, Inc. - Apache-2.0 license. Made with AI agents working in MV2's name.
import csv
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import world_diff as wd  # noqa: E402

COLS = ['id', 'country', 'provider', 'status', 'result', 'last_date', 'days_left', 'class']


def row(fid, status, result='ok', cls='', days='', last=''):
    return {'id': fid, 'country': 'US', 'provider': f'P {fid}', 'status': status, 'result': result,
            'last_date': last, 'days_left': days, 'class': cls}


# Before: groups A (inactive_running) = i1, i2, i3; B (active_stuck, <= -30 days) = mdb-2234, a2 (exactly -30);
# C (active_recent) = mdb-176 (-2), a4 (-29). i4 (inactive, expired) and a5 (active, running) are in no group.
BEFORE = [
    row('i1', 'inactive', cls='ends_within_1y', days='100', last='2027-01-30'),
    row('i2', 'inactive', cls='ends_within_30d', days='3', last='2026-10-25'),
    row('i3', 'inactive', cls='ends_within_1y', days='50', last='2026-12-11'),
    row('i4', 'inactive', cls='expired', days='-40', last='2026-09-12'),
    row('mdb-2234', 'active', cls='expired_over_1y', days='-1756', last='2021-12-31'),
    row('a2', 'active', cls='expired', days='-30', last='2026-09-22'),
    row('mdb-176', 'active', cls='expired', days='-2', last='2026-10-20'),
    row('a4', 'active', cls='expired', days='-29', last='2026-09-23'),
    row('a5', 'active', cls='ends_within_1y', days='200', last='2027-05-10'),
]
# After: i1 now active (agree); i2 still inactive and running (disagree); i3 gone; mdb-2234 unchanged (disagree);
# a2 inactive (agree); mdb-176 inactive (agree); a4 not read (unread); new1 is new and inactive_running.
AFTER = [
    row('i1', 'active', cls='ends_within_1y', days='92', last='2027-01-30'),
    row('i2', 'inactive', cls='ends_within_30d', days='5', last='2026-11-04'),
    row('i4', 'inactive', cls='expired', days='-48', last='2026-09-12'),
    row('mdb-2234', 'active', cls='expired_over_1y', days='-1764', last='2021-12-31'),
    row('a2', 'inactive', cls='expired', days='-38', last='2026-09-22'),
    row('mdb-176', 'inactive', cls='expired', days='-10', last='2026-10-20'),
    row('a4', 'active', result='network_error'),
    row('a5', 'active', cls='ends_within_1y', days='192', last='2027-05-10'),
    row('new1', 'inactive', cls='ends_within_1y', days='60', last='2026-12-29'),
]


def write(path, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=COLS)
        w.writeheader()
        w.writerows(rows)


class Groups(unittest.TestCase):
    def test_group_of(self):
        got = {r['id']: wd.group_of(r) for r in BEFORE}
        self.assertEqual(got, {'i1': 'inactive_running', 'i2': 'inactive_running', 'i3': 'inactive_running',
                               'i4': '', 'mdb-2234': 'active_stuck', 'a2': 'active_stuck',
                               'mdb-176': 'active_recent', 'a4': 'active_recent', 'a5': ''})

    def test_agrees(self):
        self.assertTrue(wd.agrees(row('x', 'future', cls='ends_within_1y', days='40')))
        self.assertFalse(wd.agrees(row('x', 'future', cls='expired', days='-1')))
        self.assertIsNone(wd.agrees(row('x', 'active', result='bad_zip')))
        self.assertIsNone(wd.agrees(row('x', 'deprecated', cls='expired', days='-1')))


class Compare(unittest.TestCase):
    def setUp(self):
        self.before = {r['id']: r for r in BEFORE}
        self.after = {r['id']: r for r in AFTER}
        self.rows, self.s = wd.compare(self.before, self.after)

    def test_outcomes(self):
        got = {r['id']: r['outcome'] for r in self.rows}
        self.assertEqual(got, {'a2': 'agree', 'a4': 'unread', 'i1': 'agree', 'i2': 'disagree', 'i3': 'gone',
                               'mdb-176': 'agree', 'mdb-2234': 'disagree'})
        o = self.s['outcomes']
        self.assertEqual(o['inactive_running'], {'feeds': 3, 'agree': 1, 'disagree': 1, 'unread': 0, 'gone': 1})
        self.assertEqual(o['active_stuck'], {'feeds': 2, 'agree': 1, 'disagree': 1, 'unread': 0, 'gone': 0})
        self.assertEqual(o['active_recent'], {'feeds': 2, 'agree': 1, 'disagree': 0, 'unread': 1, 'gone': 0})

    def test_groups_and_moves(self):
        # After: i2 and new1 inactive_running; mdb-2234 active_stuck (-1764); nothing active_recent.
        self.assertEqual(self.s['groups_before'], {'inactive_running': 3, 'active_stuck': 2, 'active_recent': 2})
        self.assertEqual(self.s['groups_after'], {'inactive_running': 2, 'active_stuck': 1, 'active_recent': 0})
        self.assertEqual(self.s['new_in_after'], 1)
        # i1 inactive>active; i2, i4 inactive>inactive; i3 inactive>gone; mdb-2234, a4, a5 active>active;
        # a2, mdb-176 active>inactive.
        self.assertEqual(self.s['status_moves'], {'active>active': 3, 'active>inactive': 2,
                                                  'inactive>inactive': 2, 'inactive>active': 1,
                                                  'inactive>gone': 1})

    def test_predictions(self):
        p = wd.score_y(self.rows, self.s)
        # Y1: A read after = i1 (agree), i2 (disagree) -> 1/2 = 0.5 < 0.6. Y2: B = mdb-2234 (disagree), a2 (agree)
        # -> 0.5 < 0.8. Y3: of NO_RANGE_IDS only mdb-2234 is followed and read: disagree, 1 of 1. Y4: mdb-176
        # agrees, mdb-3211 absent: 1 of 1. Y5: 1 + 0 = 1, outside 15-40. Y6: 2, outside 3-40.
        self.assertEqual({k: (v['value'], v['held']) for k, v in p.items()},
                         {'Y1': (0.5, False), 'Y2': (0.5, False), 'Y3': ('1 of 1', True), 'Y4': ('1 of 1', True),
                          'Y5': (1, False), 'Y6': (2, False)})

    def test_untestable(self):
        rows, s = wd.compare(self.before, {})
        p = wd.score_y(rows, s)
        self.assertIsNone(p['Y1']['held'])
        self.assertIsNone(p['Y2']['held'])
        self.assertIsNone(p['Y3']['held'])
        self.assertIsNone(p['Y4']['held'])
        self.assertEqual((p['Y5']['value'], p['Y5']['held']), (0, False))
        self.assertEqual(s['status_moves'], {'inactive>gone': 4, 'active>gone': 5})


class Main(unittest.TestCase):
    def test_end_to_end(self):
        with tempfile.TemporaryDirectory() as d:
            before = os.path.join(d, 'before', 'feeds.csv')
            write(before, BEFORE)
            write(os.path.join(d, 'after', '2026-10-29', 'feeds.csv'), BEFORE)
            write(os.path.join(d, 'after', '2026-10-30', 'feeds.csv'), AFTER)
            out = os.path.join(d, 'out')
            s = wd.main(['--before', before, '--after', os.path.join(d, 'after'), '--predictions', 'Y',
                         '--out', out])
            self.assertTrue(s['after'].endswith('2026-10-30/feeds.csv'))
            with open(os.path.join(out, 'transitions.csv'), encoding='utf-8-sig', newline='') as f:
                got = list(csv.DictReader(f))
            self.assertEqual(len(got), 7)
            self.assertEqual(list(got[0]), wd.COLUMNS)
            self.assertEqual((got[0]['id'], got[0]['group'], got[0]['after_status'], got[0]['outcome']),
                             ('a2', 'active_stuck', 'inactive', 'agree'))
            with open(os.path.join(out, 'transitions.csv'), 'rb') as f:
                raw = f.read()
            self.assertTrue(raw.startswith(b'\xef\xbb\xbf'))
            self.assertIn(b'\r\n', raw)
            with open(os.path.join(out, 'diff.json'), encoding='utf-8') as f:
                self.assertEqual(json.load(f)['predictions']['Y3']['value'], '1 of 1')
            with open(os.path.join(out, 'diff.md'), encoding='utf-8') as f:
                md = f.read()
            self.assertIn('| inactive_running | 3 | 1 | 1 | 0 | 1 |', md)
            self.assertIn('- Y1:', md)
            self.assertIn('Result: 50.0%, did not hold.', md)
            self.assertIn('Result: 1 of 1, held.', md)

    def test_after_file_and_missing(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, 'x', 'feeds.csv')
            write(p, AFTER)
            self.assertEqual(wd.resolve_after(p), p)
            self.assertEqual(wd.resolve_after(os.path.join(d, 'x')), p)
            os.makedirs(os.path.join(d, 'empty'))
            with self.assertRaises(FileNotFoundError):
                wd.resolve_after(os.path.join(d, 'empty'))


if __name__ == '__main__':
    unittest.main()
