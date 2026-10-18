# SPDX-License-Identifier: Apache-2.0
"""Behavioral controls for the actual A13 boundary and its format claim."""

import copy
import itertools
import tempfile
import unittest
from fractions import Fraction as Q
from pathlib import Path

import verify as V
from boundary import component, evaluate, interval, matrix, output_rows, summary

G = [1, 2, 4, 16, 392, 128, 162, 68, 401]


class BoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        V.authenticate()
        cls.frame = matrix(V.C.canonical_frame([45]))
        cls.source = matrix(V.logical_warp(G) + V.C.canonical_frame([45]))
        cls.final = output_rows(cls.frame, cls.source)

    def test_smallest_sharp_width(self):
        report = summary(self.final, 3)
        self.assertEqual(
            report,
            {
                "fractional_bits": 2,
                "max_norm": "5",
                "low": "-71/4",
                "high": "71/4",
                "signed_width": 8,
            },
        )
        self.assertEqual(evaluate(self.final[0], {0: 1}), Q(1, 4))

    def test_uniform_precision_formula(self):
        for precision in (3, 4, 8, 64, 128):
            report = summary(self.final, precision)
            self.assertEqual(report["signed_width"], precision + 5)
            self.assertEqual(Q(report["high"]), 5 * 2 ** (precision - 1) - Q(9, 4))

    def test_asymmetric_signed_interval_exhaustion(self):
        row = {0: Q(1, 4), 1: Q(-3, 4)}
        values = [
            evaluate(row, dict(enumerate(pair)))
            for pair in itertools.product(range(-4, 4), repeat=2)
        ]
        self.assertEqual(interval(row, 3), (min(values), max(values)))
        self.assertEqual(interval(row, 3), (Q(-13, 4), Q(15, 4)))

    def test_complex_component_signs(self):
        self.assertEqual(component({0: (Q(2), Q(3))}), {0: 2, 1: -3})
        self.assertEqual(component({0: (Q(2), Q(3))}, True), {1: 2, 0: 3})

    def test_actual_warp_is_not_logical_warp(self):
        old, new = V.C.canonical_frame([382]), V.C.canonical_frame([45])
        logical = V.logical_warp(G)
        warp = V.C.adjoint(old) + logical + new
        self.assertFalse(V.C.same_operator(warp, logical))
        self.assertTrue(V.C.same_operator(old + warp, logical + new))
        self.assertTrue(all(len(row) == 1 for row in matrix(warp)))

    def test_wrong_gaussian_sign_is_rejected(self):
        wrong = V.C.adjoint(V.C.canonical_frame([45]))
        self.assertNotEqual(matrix(wrong), self.frame)
        with self.assertRaisesRegex(ValueError, "operator equality"):
            V.integer_check(wrong, self.frame)

    def test_omitted_climb_changes_range(self):
        identity = matrix([])
        wrong = output_rows(identity, self.source)
        self.assertNotEqual(wrong, self.final)
        self.assertEqual(summary(wrong, 64)["max_norm"], "3")

    def test_source_alignment_needs_quarter_grid(self):
        values = [
            q
            for row in self.source
            for im in (False, True)
            for q in component(row, im).values()
        ]
        self.assertTrue(
            all((q * 4).denominator == 1 and int(q * 4) % 2 == 0 for q in values)
        )
        self.assertTrue(any(int(q * 2) % 2 for q in values))

    def test_inverse_frame_returns_exact_target(self):
        new = V.C.canonical_frame([45])
        self.assertEqual(matrix(new + V.C.adjoint(new)), matrix([]))

    def test_invalid_capacities(self):
        with self.assertRaisesRegex(ValueError, "bounded local circuit"):
            matrix([("C", 1, 1)] * 21)
        with self.assertRaisesRegex(ValueError, "input precision"):
            summary(self.final, 2)
        with self.assertRaisesRegex(ValueError, "invertible permutation"):
            matrix([("P", [0] * 9)])

    def test_warped_prefix_dependencies_are_retained(self):
        events = [
            ["warp", ["L", 1], 7, 0, 0],
            ["scalar", ["add", ["L", 0], ["L", 1], 1, 2], 0],
        ]
        rows = V.prefix_rows(events)
        self.assertEqual(rows[0], {(0, ()): 1, (1, (7,)): Q(1, 2)})
        rows = V.prefix_rows([*events[:1], ["warp", ["L", 1], -7, 0, 0]])
        self.assertEqual(rows[1], {(1, ()): 1})

    def test_phase_does_not_rewrite_earlier_observation(self):
        trace = []
        identity = ("P", [1 << i for i in range(9)])
        phase = ("D", [0] * 9, [2] + [0] * 8)
        final = matrix([identity, phase], observations=trace)
        self.assertEqual(trace[0][2][1], {1: (1, 0)})
        self.assertEqual(final[1], {1: (-1, 0)})

    def test_actual_trace_matches_fresh_prefixes(self):
        old, new = V.C.canonical_frame([382]), V.C.canonical_frame([45])
        warp = V.C.adjoint(old) + V.logical_warp(G) + new
        initial, trace = matrix(old), []
        matrix(warp, initial, trace)
        for index, kind, rows in trace:
            if kind == "endpoint":
                self.assertEqual(rows, matrix(warp[: index + 1], initial))

    def test_native_bit_caller_extrema(self):
        result = summary(self.final, 3)
        fixtures = V.witnesses(self.final, 3, result)
        checked = V.literal_half_add(self.final, self.source, fixtures, 8)
        self.assertEqual(checked["fixtures"]["high"]["output"], 71)
        self.assertEqual(checked["fixtures"]["low"]["output"], -71)
        self.assertEqual(checked["gates_per_real_component"], 53)
        self.assertEqual(checked["clean_carries_returned"], 7)

    def test_source_bound_semantic_mutations(self):
        inherited, produce, parent = V.load_parent()
        raw = inherited.read(V.PACKAGE / "vendor/parent/vendor/WORD-base.json.gz")
        word = produce(
            parent(raw), inherited.read(V.PACKAGE / "vendor/parent/EDITS.json")
        )
        with tempfile.TemporaryDirectory(
            prefix="rank7-boundary-controls-"
        ) as directory:
            work = Path(directory) / "native"
            programs, _ = inherited.compile_word(word, work)
            canonical = inherited.read(work / "native/CANONICAL-WORD.json.gz")
            self.assertEqual(V.bind(canonical, programs["forward"]), (G, 6685))
            wrong = copy.deepcopy(canonical)
            wrong["A"][13][3] = 1
            with self.assertRaisesRegex(ValueError, "literal A13"):
                V.bind(wrong, programs["forward"])
            wrong = copy.deepcopy(programs["forward"])
            wrong[6685][1][3] = 1
            with self.assertRaisesRegex(ValueError, "adjacent emitted boundary"):
                V.bind(canonical, wrong)
            wrong = copy.deepcopy(programs["forward"])
            wrong[252][1][3] = 1
            with self.assertRaisesRegex(ValueError, "dirty target prefix"):
                V.bind(canonical, wrong)
            wrong = copy.deepcopy(programs["forward"])
            index = wrong.index(["phase", "A"])
            wrong[index:index] = [
                ["warp", ["L", 166], 52, 0, 0],
                ["scalar", ["add", ["L", 126], ["L", 166], 1, 1], 0],
                ["warp", ["L", 166], -52, 0, 0],
                ["scalar", ["add", ["L", 126], ["L", 166], -1, 1], 0],
            ]
            with self.assertRaisesRegex(ValueError, "dirty target prefix"):
                V.bind(canonical, wrong)


if __name__ == "__main__":
    unittest.main()
