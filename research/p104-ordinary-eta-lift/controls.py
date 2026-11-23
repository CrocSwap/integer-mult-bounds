#!/usr/bin/env python3
"""Independent boundary and corrupted-source controls for the replay."""

from fractions import Fraction as Q
import json
from pathlib import Path
from shutil import copytree
import sys
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import setup_scaling
import witness


class BoundaryControls(unittest.TestCase):
    def test_exact_three_stage_and_neighbor(self):
        # Recompute the rational recurrence directly from the source prices.
        raw, debit = Q(4391986206293, 2**50), Q(11239, 8192)
        eta, q = Q(1, 256), Q("0.003900000000000005")
        previous = Q(0)
        for height in (8192, 106000):
            upper = min(eta, (249 * (raw - debit / height) + previous) / 250)
            booked = Q((upper * 10**21).__floor__() - 1, 10**21)
            self.assertLess(previous, booked)
            self.assertLess(booked, upper)
            previous = booked
        price = lambda h: (249 * (raw - debit / h) + previous) / 250
        self.assertLess(price(1681000), q)
        self.assertGreater(price(1681001), q)
        self.assertLess(min(Q(39, 10000), price(1681001)), q)
        self.assertLess(price(524288), q)
        saved = json.loads((HERE / "RESULT.json").read_bytes())
        self.assertEqual(Q(saved["ordinary_target"]), q)
        self.assertEqual(Q(saved["stage_rates"][1]["booked"]), previous)

    def test_gaussian_rejects_target(self):
        q = Q("0.003900000000000005")
        raw = Q(17145637307, 2**42)
        priced = raw - Q(64939, 524288 * 490950)
        self.assertLess(priced, raw)
        self.assertLess(raw, q)
        saved = json.loads((HERE / "RESULT.json").read_bytes())
        self.assertTrue(saved["target_combined_rejected"])
        self.assertEqual(Q(saved["gaussian_priced"]), priced)

    def test_25_bit_height_and_action_guards(self):
        self.assertTrue(setup_scaling.safe_height(1024))
        self.assertFalse(setup_scaling.safe_height(1023))
        self.assertTrue(setup_scaling.safe_height(2**25 - 1))
        self.assertFalse(setup_scaling.safe_height(2**25))
        profile = SimpleNamespace(kappa=Q(389846, 10**8), eta=Q(39, 10000),
                                  positive_stop_denominator=10**18)
        self.assertTrue(setup_scaling.bounded_scalars(profile))
        profile.positive_stop_denominator = 2**128
        self.assertFalse(setup_scaling.bounded_scalars(profile))
        extra = 2 * 2048 * (2**25 + 1) + 7 * 2**24
        self.assertLess(extra, 2**40)
        self.assertLess(setup_scaling.action_envelope()["transition_upper"], 2**228)

    def test_corrupted_pinned_sources_are_rejected(self):
        with TemporaryDirectory(prefix="ordinary-corrupt-") as tmp:
            base = Path(tmp)
            copytree(witness.ORIGINAL, base / "original")
            previous = witness.ORIGINAL
            witness.ORIGINAL = base / "original"
            try:
                for name in ("prepare.py", "PEER-SOURCE.json", "peer8057.tar.gz", "source-pins.json"):
                    with self.subTest(name=name):
                        path = witness.ORIGINAL / name
                        before = path.read_bytes()
                        path.write_bytes(before[:-1] + bytes([before[-1] ^ 1]))
                        with self.assertRaises(AssertionError):
                            witness.source_runtime(base / "tree")
                        path.write_bytes(before)
            finally:
                witness.ORIGINAL = previous


if __name__ == "__main__":
    if not __debug__:
        raise ValueError("Run with assertions enabled")
    unittest.main(verbosity=2)
