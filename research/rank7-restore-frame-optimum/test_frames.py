# SPDX-License-Identifier: Apache-2.0
"""Behavioral fixtures distinguish genuine optimization from a fixed PASS result."""

import copy
import unittest
from pathlib import Path
from unittest.mock import patch

from frames import ZERO, bounds, census, domain, edge_profile, problem, registers, space
from verify import distribution, load_words, run


class FrameTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.words = load_words()

    def test_improvable_one_gate_fixture(self):
        line, plane = space([1]), space([1, 2])
        result = census([["scale", 0, -1, 1, [1]]],
                        {0: [(-1, ZERO), (0, line), (1, plane)]})
        self.assertEqual(result["global_legal"], 5)
        self.assertEqual(result["components"][0]["deltas"], [
            {"profile": {}, "count": 3},
            {"profile": {1: -2, 2: 1}, "count": 2}])
        with self.assertRaisesRegex(ValueError, "nonnegative multiple"):
            distribution(result)

    def test_coordinated_frames_and_containment(self):
        line, plane = space([1]), space([1, 2])
        gates = [["add", 0, 1, 1, 1, [1]]] * 2
        events = [(-1, ZERO), (0, line), (1, line), (2, plane)]
        result = census(gates, {0: events, 1: events})
        self.assertEqual(result["component_attempts"], 25)
        self.assertEqual(result["global_legal"], 12)
        self.assertEqual(result["components"][0]["gates"], [0, 1])
        self.assertEqual(result["components"][0]["deltas"], [
            {"profile": {}, "count": 9},
            {"profile": {1: -4, 2: 2}, "count": 3}])

    def test_independent_components_multiply(self):
        line, plane = space([1]), space([1, 2])
        gates = [["scale", r, -1, 1, [1]] for r in (0, 1)]
        traces = {r: [(-1, ZERO), (r, line), (2, plane)] for r in (0, 1)}
        result = census(gates, traces)
        self.assertEqual(result["component_attempts"], 10)
        self.assertEqual(result["global_legal"], 25)
        self.assertEqual([row["gates"] for row in result["components"]], [[0], [1]])

    def test_rotated_subspaces_are_included(self):
        self.assertEqual(set(domain(ZERO, space([1, 2]))),
                         {ZERO, space([1]), space([2]), space([3]), space([1, 2])})

    def test_equal_rank_wrong_axis_rejects(self):
        self.assertIsNone(edge_profile([(0, -1, space([1]), 0, space([2]))], {}))

    def test_incompatible_endpoints_reject(self):
        with self.assertRaisesRegex(ValueError, "frame interval bound"):
            bounds([["scale", 0, -1, 1, [1]]],
                   {0: [(-1, space([2])), (0, space([1])), (1, space([1]))]})

    def test_resource_and_input_limits(self):
        for vectors in ([512], [0], [True], list(range(1, 11))):
            with self.subTest(vectors=vectors), self.assertRaises(ValueError):
                space(vectors)
        with self.assertRaisesRegex(ValueError, "domain quotient"):
            domain(ZERO, space([1, 2, 4]))
        for gate in (["add", 0, 0, 1, 1, []], ["scale", 0, 1, 0, []],
                     ["scale", 704, 1, 1, []], ["unknown", 0, 1, 1, []]):
            with self.subTest(gate=gate), self.assertRaises(ValueError):
                registers(gate)

    def test_source_hash_is_checked(self):
        original = Path.read_bytes

        def changed(path):
            raw = original(path)
            return raw + b"x" if path.name == "base.json.gz" else raw

        with patch.object(Path, "read_bytes", changed), self.assertRaisesRegex(
            ValueError, "pinned exported input bytes"
        ):
            load_words()

    def test_changed_frame_and_stale_invoice_reject(self):
        word = copy.deepcopy(self.words["base"])
        word["restore"][162][-1] = [1, 2, 4, 8, 16, 32, 64]
        with self.assertRaisesRegex(ValueError, "nonmonotone frame"):
            problem(word)
        word = copy.deepcopy(self.words["base"])
        word["report"]["local_profile"]["1"] -= 1
        with self.assertRaisesRegex(ValueError, "complete declared local profile"):
            problem(word)

    def test_false_helper_width_rejects(self):
        word = copy.deepcopy(self.words["base"])
        word["report"]["width_inventory"]["9"] -= 1
        with self.assertRaisesRegex(ValueError, "declared helper widths"):
            problem(word)

    def test_complete_source_census(self):
        result = run()
        self.assertEqual(result["status"], "PASS_RESTORE_FRAME_OPTIMUM")
        for provider in result["providers"].values():
            self.assertEqual(provider["global_legal"], 2160000)
            self.assertEqual(provider["optimum_assignments"], 32)
            self.assertEqual(provider["delta_units"][9], 11664)


if __name__ == "__main__":
    unittest.main()
