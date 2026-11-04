"""Tests for export_check.py (no network). MV2 of Munim, Inc. Made with AI agents working in MV2's name. Apache-2.0."""
import unittest

import export_check as E

BEFORE = """id,status,class
mdb-176,active,expired
mdb-3211,active,expired
mdb-3149,inactive,ends_within_1y
mdb-1956,inactive,ends_within_30d
mdb-1,active,ends_within_1y
mdb-2,inactive,expired
mdb-9,active,ends_within_1y
mdb-3,inactive,expired_over_1y
mdb-4,active,expired_over_1y
mdb-5,inactive,
"""

AFTER = """id,data_type,status
mdb-176,gtfs,inactive
mdb-3211,gtfs,inactive
mdb-3149,gtfs,active
mdb-1956,gtfs,active
mdb-1,gtfs,active
mdb-2,gtfs,inactive
mdb-3,gtfs,inactive
mdb-4,gtfs,active
mdb-5,gtfs,inactive
mdb-7,gbfs,active
"""


class CompareTest(unittest.TestCase):
    def test_compare(self):
        r = E.compare(E.rows_of(BEFORE), E.rows_of(AFTER))
        self.assertEqual(r["before"], 10)
        self.assertEqual(r["after_gtfs"], 9)
        self.assertEqual(r["missing_after"], 1)  # mdb-9
        self.assertEqual(r["status_changed"], 4)
        self.assertEqual(r["moves"], {"active->active": 2, "active->inactive": 2, "inactive->active": 2,
                                      "inactive->inactive": 3})
        # mdb-3 (inactive, expired over a year ago) agrees; mdb-4 (active, expired over a year ago) does not;
        # mdb-5 (no class: not read) is not counted.
        self.assertEqual(r["disagreeing_before"], 5)
        self.assertEqual(r["of_those_now_agree_with_their_10_29_calendar"], 4)
        self.assertEqual(r["now_agree_ids"], ["mdb-176", "mdb-1956", "mdb-3149", "mdb-3211"])
        self.assertEqual(r["named"], {"mdb-176": "inactive", "mdb-3211": "inactive", "mdb-3149": "active",
                                      "mdb-1956": "active"})
        self.assertEqual(E.checks(r), {"C1": "held", "C2": "held"})

    def test_classes(self):
        self.assertTrue(E.is_expired("expired_over_1y"))
        self.assertFalse(E.disagrees("inactive", "expired_over_1y"))
        self.assertTrue(E.disagrees("active", "expired_over_1y"))
        self.assertTrue(E.disagrees("inactive", "ends_after_2y"))
        self.assertFalse(E.disagrees("future", "ends_within_1y"))

    def test_nothing_moved(self):
        r = E.compare(E.rows_of(BEFORE), E.rows_of(BEFORE))
        self.assertEqual(r["status_changed"], 0)
        self.assertEqual(E.checks(r), {"C1": "did not hold", "C2": "did not hold"})

    def test_bom_and_day(self):
        self.assertEqual(E.rows_of("﻿id,status\nx,active\n".lstrip("﻿"))[0]["id"], "x")
        self.assertEqual(E.export_day_of("Fri, 30 Oct 2026 04:12:00 GMT"), "2026-10-30")
        self.assertIsNone(E.export_day_of(None))
        self.assertIsNone(E.export_day_of("yesterday"))


if __name__ == "__main__":
    unittest.main()
