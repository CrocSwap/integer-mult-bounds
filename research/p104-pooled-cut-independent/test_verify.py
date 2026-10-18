#!/usr/bin/env python3
"""Small exhaustive and mutation controls, with no full P104 replay."""

import itertools
import runpy
import unittest
from pathlib import Path
from unittest.mock import patch

V = runpy.run_path(str(Path(__file__).with_name("verify.py")))


def small_spaces():
    spaces = {frozenset({0})}
    for size in range(1, 4):
        for basis in itertools.combinations(range(1, 8), size):
            generated = {0}
            for v in basis:
                generated |= {p ^ v for p in tuple(generated)}
            spaces.add(frozenset(generated))
    return sorted(spaces, key=lambda s: (len(s), sorted(s)))


class Controls(unittest.TestCase):
    def test_all_small_interval_contacts(self):
        spaces = small_spaces()
        self.assertEqual(len(spaces), 16)
        for d in range(4):
            bounds = [
                (a, b)
                for a in spaces
                for b in spaces
                if a <= b and len(a) <= 2**d <= len(b)
            ]
            actual = V["interval_relation"](bounds, d)
            for i, (a, b) in enumerate(bounds):
                frames = {f for f in spaces if len(f) == 2**d and a <= f <= b}
                for j, (c, e) in enumerate(bounds):
                    common = any(c <= f <= e for f in frames)
                    self.assertEqual(bool((actual[i] >> j) & 1), common)

    def test_same_layer_fresh_read_and_multiple_sources(self):
        # Three actual equal frames. The source is read during this same layer.
        state = V["transfer"]([0, 0, 0], [1, 2, 0], [7, 7, 7])
        self.assertEqual(state, [3, 3, 3])
        # Reading only after contacts is strictly weaker on this input shape.
        self.assertEqual(V["transfer"]([0, 0, 0], [0, 0, 0], [7, 7, 7]), [0, 0, 0])

    def test_component_closure_is_strictly_more_optimistic(self):
        line1, line2 = frozenset({0, 1}), frozenset({0, 2})
        bounds = [(line1, line1), (frozenset({0}), frozenset(range(8))), (line2, line2)]
        relation = V["interval_relation"](bounds, 1)
        self.assertEqual(relation, [3, 7, 6])
        self.assertEqual(V["transfer"]([1, 0, 0], [0, 0, 0], relation), [1, 1, 0])
        # A connected-component implementation would incorrectly take two hops.
        self.assertEqual(V["transfer"]([1, 1, 0], [0, 0, 0], relation), [1, 1, 1])

    def test_all_actual_equal_frame_components(self):
        # Every assignment of three actual F2^3 frames has clique components.
        spaces = small_spaces()
        for assigned in itertools.product(spaces, repeat=3):
            relation = [
                sum(1 << j for j, g in enumerate(assigned) if f == g) for f in assigned
            ]
            for seed in range(3):
                source = [int(i == seed) for i in range(3)]
                expected = [int(f == assigned[seed]) for f in assigned]
                self.assertEqual(V["transfer"](source, [0, 0, 0], relation), expected)

    def test_bad_basis_and_dimension(self):
        for basis in ([0], [512], [1, 1], [1, 2, 3]):
            with self.assertRaises(ValueError):
                V["points"](basis)
        with self.assertRaises(ValueError):
            V["bounds_at"](([], [], [], [], []), 9)

    def test_source_hash_and_duplicate_key_reject(self):
        globals_ = V["load_inputs"].__globals__
        real = globals_["read_json"]

        def corrupt(path):
            result = real(path)
            if path.name == "SOURCES.json":
                for row in result["files"]:
                    if row["usage"] == "input":
                        row["sha256"] = "0" * 64
            return result

        with (
            patch.dict(globals_, {"read_json": corrupt}),
            self.assertRaisesRegex(ValueError, "source hash"),
        ):
            V["load_inputs"]()
        with self.assertRaises(ValueError):
            V["pairs_unique"]([("x", 1), ("x", 2)])

    def test_coefficient_binding_rejects_changed_geometry(self):
        _, _, fixture = V["load_inputs"]()
        fixture["section4_explicit_P104"]["F0"] = []
        with self.assertRaises(ValueError):
            V["required_masks"](fixture)


if __name__ == "__main__":
    unittest.main()
