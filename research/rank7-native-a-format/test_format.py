# SPDX-License-Identifier: Apache-2.0
"""Behavioral controls on genuine emitted streams and the native format lemma."""

import copy
import json
import os
import tempfile
import unittest
from fractions import Fraction as Q
from pathlib import Path

from check_integer import trace
from format import Ledger, capacity, fourier_controls, stage
from numerators import controls, partials
from verify import PACKAGE, authenticate, run


class FormatTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix="native-A-tests-")
        cls.root = Path(cls.temp.name)
        cls.result = run(cls.root)
        from replay_parent import read

        cls.word = read(cls.root / "base/native/CANONICAL-WORD.json.gz")
        cls.events = read(cls.root / "base/native/LOCAL-PROGRAMS.json.gz")["forward"]
        cls.expected = cls.result["providers"]["base"]["streams"]["forward"]

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_genuine_both_providers_and_orientations(self):
        expected = json.loads((PACKAGE / "RESULT.json").read_text())
        self.assertEqual(self.result, expected)
        for provider in self.result["providers"].values():
            for direction, report in provider["streams"].items():
                self.assertEqual(report["gatewise"]["signed_width"], 89)
                self.assertEqual(
                    report["paired"]["signed_width"],
                    83 if direction == "forward" else 82,
                )
                self.assertEqual(
                    report["pair_first"]["signed_width"],
                    82 if direction == "forward" else 81,
                )
                self.assertEqual(
                    report["counts"],
                    {
                        "A_climbs": 1020,
                        "A_scalars": 4028,
                        "A_warps": 24,
                        "prelude_scalars": 5964,
                        "prelude_warps": 72,
                    },
                )

    def test_fourier_pairing_and_conjugation(self):
        reports = fourier_controls()
        for r, report in enumerate(reports):
            coefficients = [complex(1)]
            for _ in range(r):
                coefficients = [
                    z * complex(1, s) / 2 for z in coefficients for s in (-1, 1)
                ]
            for conjugate in (False, True):
                row = [z.conjugate() if conjugate else z for z in coefficients]
                self.assertEqual(
                    sum(abs(z.real) + abs(z.imag) for z in row), 2 ** ((r + 1) // 2)
                )
                self.assertTrue(
                    all(
                        (z.real * 2 ** report["grid"]).is_integer()
                        and (z.imag * 2 ** report["grid"]).is_integer()
                        for z in row
                    )
                )

    def test_correlated_pair_first_numerators(self):
        reports = controls()
        self.assertEqual(len(reports), 36)
        forward = [4, 4, 8, 8, 16, 16, 32, 32, 64]
        inverse = [2, 4, 4, 8, 8, 16, 16, 32, 32]
        for report in reports:
            expected = (inverse if report["inverse"] else forward)[report["rank"] - 1]
            self.assertEqual(report["partial_norm"], expected)
            rows = partials(report["rank"], report["inverse"], report["orientation"])
            self.assertTrue(
                all(sum(map(abs, row.values())) <= expected for row in rows)
            )
        report = self.expected["pair_first"]
        self.assertTrue(capacity(report, 64, 7, 84))
        with self.assertRaisesRegex(ValueError, "strict symmetric"):
            capacity(report, 64, 7, 83)

    def test_positive_signed_limit_needs_extra_bit(self):
        ledger = Ledger(True)
        report = ledger.result(64)
        self.assertEqual(report["signed_width"], 65)
        with self.assertRaisesRegex(ValueError, "strict symmetric"):
            capacity(report, 64, 0, 64)

    def test_insufficient_grid_and_capacity(self):
        report = self.expected["paired"]
        for grid, width, error in ((4, 83, "common grid"), (5, 82, "strict symmetric")):
            with self.assertRaisesRegex(ValueError, error):
                capacity(report, 64, grid, width)
        self.assertTrue(capacity(report, 64, 7, 85))

    def test_literal_C_numerator_evenness(self):
        # Independent signed integer inputs; all axes act on distinct bits.
        for rank in range(1, 10):
            grid = (rank + 1) // 2
            unit = 1 << grid
            field = [
                ((x * 17 % 31 - 15) * unit, (x * 7 % 23 - 11) * unit)
                for x in range(1 << rank)
            ]
            for axis in range(rank):
                new = []
                for x, (a, b) in enumerate(field):
                    c, d = field[x ^ (1 << axis)]
                    numerator = (a - b + c + d, a + b + d - c)
                    self.assertTrue(all(n % 2 == 0 for n in numerator))
                    new.append(tuple(n // 2 for n in numerator))
                field = new

    def test_frame_mismatch(self):
        events = copy.deepcopy(self.events)
        i = next(i for i, e in enumerate(events) if e[0] == "climb")
        events[i][3] = 999
        with self.assertRaisesRegex(ValueError, "climb frames"):
            stage(events, self.word)

    def test_missing_climb(self):
        events = copy.deepcopy(self.events)
        i = next(i for i, e in enumerate(events) if e[0] == "climb")
        del events[i]
        with self.assertRaisesRegex(ValueError, "frame"):
            stage(events, self.word)

    def test_unbound_warp(self):
        events = copy.deepcopy(self.events)
        i = next(i for i, e in enumerate(events) if e[0] == "warp")
        events[i][2] = 999
        with self.assertRaisesRegex(ValueError, "declared logical warp"):
            stage(events, self.word)

    def test_nondyadic_source_and_alias(self):
        for denominator, alias, error in ((3, False, "dyadic"), (2, True, "distinct")):
            events = copy.deepcopy(self.events)
            gate = next(e[1] for e in events if e[0] == "scalar" and e[1][0] == "add")
            gate[3:5] = [1, denominator]
            if alias:
                gate[2] = gate[1].copy()
            with self.assertRaisesRegex(ValueError, error):
                stage(events, self.word)

    def test_semantic_sign_change_is_visible(self):
        events = copy.deepcopy(self.events)
        gate = next(e[1] for e in events if e[0] == "scalar" and e[1][0] == "add")
        gate[3] *= -1
        changed = stage(events, self.word)
        self.assertNotEqual(
            changed["prefix_rows_sha256"], self.expected["prefix_rows_sha256"]
        )
        self.assertEqual(trace(events), changed["prefix_rows_sha256"])

    def test_truncated_stage(self):
        with self.assertRaisesRegex(ValueError, "complete A"):
            stage(self.events[:100], self.word)
        with self.assertRaisesRegex(ValueError, "missing integer"):
            trace(self.events[:100])

    def test_source_corruption(self):
        import verify

        frozen = self.root / "source-control"
        frozen.mkdir()
        (frozen / "vendor").mkdir()
        (frozen / "vendor/a").write_text("changed")
        (frozen / "VENDOR.json").write_text(
            json.dumps({"files": [{"path": "vendor/a", "sha256": "0" * 64}]})
        )
        original = verify.PACKAGE
        try:
            verify.PACKAGE = frozen
            with self.assertRaisesRegex(ValueError, "source bytes"):
                authenticate()
        finally:
            verify.PACKAGE = original

    def test_parameter_limits(self):
        for p in (2, 129, True):
            with self.assertRaisesRegex(ValueError, "input precision"):
                stage(self.events, self.word, p)
        with self.assertRaisesRegex(ValueError, "capacity observation"):
            Ledger(True).observe(65, Q(1), 0, "bad")


if __name__ == "__main__":
    # Explicitly consume TMPDIR through TemporaryDirectory; no checkout outputs.
    if os.environ.get("PYTHONDONTWRITEBYTECODE") is None:
        os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
    unittest.main()
