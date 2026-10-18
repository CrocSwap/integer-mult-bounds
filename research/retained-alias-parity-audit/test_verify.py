#!/usr/bin/env python3
"""Failure and premise controls for the retained-alias audit; Apache-2.0."""

import importlib.util
import itertools
from pathlib import Path
import struct
import tempfile
import unittest

SPEC = importlib.util.spec_from_file_location("alias_audit", Path(__file__).with_name("verify.py"))
audit = importlib.util.module_from_spec(SPEC)
# Compile the neighboring source directly, bypassing any preexisting .pyc.
exec(compile(Path(SPEC.origin).read_bytes(), SPEC.origin, "exec", optimize=0), audit.__dict__)


class Controls(unittest.TestCase):
    def test_alias_cancellation_and_distinct_helper_control(self):
        row = [0, 0, 1, 1]
        self.assertEqual(audit.direct_scatter([0, 0], row, [1]), (0, 0))
        self.assertEqual(audit.discrepancy([0, 0], row), [])
        self.assertEqual(audit.direct_scatter([0, 1], row, [1, 2]), (0, 3))
        self.assertEqual(audit.discrepancy([0, 1], row), [0, 1])

    def test_injective_case_recovers_odd_multiplicity(self):
        for length in range(6):
            for row in itertools.product(range(3), repeat=length):
                odd = all(row.count(k) % 2 for k in set(row))
                self.assertEqual(not audit.discrepancy([0, 1, 2], row), odd)

    def test_independence_premise_is_needed(self):
        # Dropping arbitrary-input/invertible-prefix premises allows distinct
        # registers with equal values. Address injectivity alone then fails.
        row = [0, 0, 1, 1]
        self.assertTrue(audit.discrepancy([0, 1], row))
        self.assertEqual(audit.direct_scatter([0, 1], row, [5, 5]), (0, 0))

    def test_minimal_length_four(self):
        for length in range(4):
            for row in itertools.product(range(3), repeat=length):
                if any(row.count(k) % 2 == 0 for k in set(row)):
                    self.assertTrue(audit.discrepancy([0, 0, 0], row))

    def test_source_corruption_fails_before_execution(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            sources = audit.json.loads((audit.PACKAGE / "SOURCES.json").read_bytes())
            for pin in sources["files"]:
                if pin["usage"] == "input":
                    target = root / pin["path"]
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes((audit.ROOT / pin["path"]).read_bytes())
            path = root / audit.EXPORTER
            path.write_bytes(path.read_bytes() + b"\n# changed source\n")
            with self.assertRaisesRegex(ValueError, "source mismatch"):
                audit.authenticated(root)

    def test_record_lifetimes_and_truncation_fail(self):
        pack = lambda *e: struct.pack("<6i", *e)
        copy = pack(2, 0, 2, 1, 0, 7)
        erase = pack(3, 0, 2, 1, 0, 0)
        self.assertEqual(audit.record_replay(copy + erase, 2), ([1, 2], [7]))
        for invalid in (copy, copy + erase[:-1], erase, pack(9, 0, 0, 0, 0, 0)):
            with self.assertRaises(ValueError):
                audit.record_replay(invalid, 2)


if __name__ == "__main__":
    unittest.main()
