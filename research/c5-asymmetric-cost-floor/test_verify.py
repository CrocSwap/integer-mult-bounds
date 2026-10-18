#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 thakrarsagar. Developed with substantial OpenAI Codex assistance.
"""Behavioral controls for the scoped asymmetric support certificate."""

from fractions import Fraction
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("c5_asymmetric_verify", HERE / "verify.py")
v = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(v)


class CertificateControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _, planes = v.load_geometry()
        cls.planes = v.core(planes)
        cls.records = {(r.left, r.right): r for r in v.support_records(cls.planes)}

    def test_exact_fit_signed_asymmetric_terms_and_forbidden_entries(self):
        # Independently construct the five disjoint, free-adjacent port pairs.
        terms = []
        for source, target in ((1, 2), (3, 4), (5, 6), (7, 8), (9, 0)):
            vector = tuple(int(j in (source, target)) for j in range(10))
            terms.append((Fraction(1), vector, vector))
        self.assertEqual(v.check_fit(self.planes, terms), 20)

        # Cancellation is legal with signed, unequal source/target supports.
        # Each added term has full-plane tariff one, regardless of its weight.
        left = tuple(int(j == 4) for j in range(10))
        right = tuple(int(j in (0, 8)) for j in range(10))
        cancelling = [(Fraction(3, 2), left, right), (Fraction(-3, 2), left, right)]
        self.assertEqual(v.check_fit(self.planes, terms + cancelling), 22)

        wrong_diagonal = list(terms)
        wrong_diagonal[0] = (Fraction(1, 2), terms[0][1], terms[0][2])
        unit = lambda i: tuple(int(j == i) for j in range(10))
        for label, invalid in (
            ("diagonal", wrong_diagonal),
            ("same-plane off-diagonal", terms + [(1, unit(0), unit(1))]),
            ("nonorthogonal-plane entry", terms + [(1, unit(0), unit(4))]),
        ):
            with self.subTest(label=label):
                with self.assertRaisesRegex(ValueError, "strict scalar mask"):
                    v.check_fit(self.planes, invalid)

    def test_all_principal_rank_counts_at_nineteen_fail_termwise_trace(self):
        masks = ((28, 28), (19, 19), (7, 7), (14, 24), (1, 4))
        witness = [self.records[pair] for pair in masks]
        tight = (4, 4, 4, 4, 2, 2, 2)
        self.assertEqual(sum(r.cost for r in witness), 19)
        self.assertEqual(tuple(sum(r.hits[i] for r in witness) for i in range(6)),
                         tight[:6])
        self.assertEqual(sum(r.defect for r in witness), 2)
        self.assertEqual(sum(r.missing for r in witness), 4)
        # This stronger false candidate passes every forced principal I4 and
        # every singleton I2 count, rather than only the seven proof blocks.
        for i, j in ((0, 2), (0, 3), (1, 3), (1, 4), (2, 4)):
            block = (1 << i) | (1 << j)
            self.assertGreaterEqual(sum(bool(a & block) and bool(b & block)
                                        for a, b in masks), 4)
        for i in range(5):
            self.assertGreaterEqual(sum(bool(a & b & (1 << i)) for a, b in masks), 2)
        self.assertEqual([(r.left, r.right) for r in witness
                          if not v.trace_compatible(r, tight)],
                         [(19, 19), (7, 7), (14, 24), (1, 4)])

        # Only these five unique patterns are searched: the full ten-case
        # enumeration is checked separately by the independent implementation.
        patterns = tuple(dict.fromkeys(witness))
        self.assertTrue(v.search_case(patterns, tight, use_trace=False)["reachable"])
        self.assertFalse(v.search_case(patterns, tight)["reachable"])

    def test_excess_rank_block_does_not_force_individual_trace_one(self):
        # These disjoint supports hit Q0 but have no possible nonzero z_i.
        record = self.records[(4, 1)]
        self.assertEqual(record.hits, (1, 0, 0, 0, 0, 0))
        self.assertFalse(v.trace_compatible(record, (4, 4, 4, 4, 2, 2, 0)))
        self.assertTrue(v.trace_compatible(record, (5, 4, 4, 4, 2, 2, 0)))

    def test_unbounded_pattern_reuse_missing_count_saturation_and_free_terms(self):
        # A real support profile, with artificial small count targets, isolates
        # the reachability engine from the theorem's ten physical slack cases.
        step, free = self.records[(4, 17)], self.records[(1, 2)]
        self.assertEqual(step.hits, (1, 0, 0, 0, 0, 0))
        self.assertEqual((step.defect, step.missing), (0, 1))
        self.assertEqual((free.cost, free.hits, free.defect, free.missing),
                         (0, (0, 0, 0, 0, 0, 0), 0, 0))
        for repetitions, expected in ((3, False), (4, True), (5, True)):
            with self.subTest(repetitions=repetitions):
                target = (repetitions, 0, 0, 0, 0, 0, 0)
                result = v.search_case((step, free), target, use_trace=False)
                self.assertEqual(result["reachable"], expected)
        with self.assertRaisesRegex(ValueError, "zero-price record must have zero increments"):
            v.search_case((free._replace(missing=1),), (0,) * 7, use_trace=False)

    def test_source_byte_change_is_rejected_before_geometry_use(self):
        changed = v.ROOT / "research/c5-dyadic-decoder-gate/inputs/MATCHING.json"
        original_read = Path.read_bytes
        touched = []

        def altered_read(path):
            raw = original_read(path)
            if path == changed:
                touched.append(path)
                return raw + b"\n"  # Still valid JSON; byte authentication must fail.
            return raw

        with patch.object(Path, "read_bytes", altered_read):
            with self.assertRaisesRegex(ValueError, "source bytes changed.*MATCHING.json"):
                v.load_geometry()
        self.assertEqual(touched, [changed])


if __name__ == "__main__":
    unittest.main()
